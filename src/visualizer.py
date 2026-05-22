"""
# 1. 功能
matplotlib 可视化模块。将仿真轨迹和快照序列渲染为 GIF 动画。
支持 2D 和 3D（通过 Z 切片投影）。

# 2. 输入
- trajectory: list[list[(x, y, z)]]
- snapshots: list[np.ndarray] — 2D 或 3D 快照
- slice_z: 3D 时渲染的 Z 切片深度（None = 自动取中间层）

# 3. 输出
- GIF 文件

# 4. 核心执行流程
1. 检测快照维度
2. 3D 时：提取 slice_z 层的 XY 切片作为目标，过滤附近无人机
3. 逐帧绘制，合成 GIF

# 5. 依赖
- numpy, matplotlib, PIL
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def render_gif(
    trajectory: list[list[tuple[float, ...]]],
    snapshots: list[np.ndarray],
    output_path: str = "swarm.gif",
    fps: int = 5,
    drone_size: int = 60,
    slice_z: int | None = None,
) -> str:
    """将仿真轨迹渲染为 GIF 动画。

    Args:
        trajectory: trajectory[t][i] = (x, y, z)
        snapshots: 2D (H, W) 或 3D (D, H, W) 快照
        output_path: 输出路径
        fps: 帧率
        drone_size: 点大小
        slice_z: 3D 时渲染的 Z 切片，None 取中间层

    Returns:
        输出文件路径
    """
    if not trajectory or not snapshots:
        raise ValueError("trajectory 和 snapshots 不能为空")

    n_frames = len(trajectory)
    is_3d = snapshots[0].ndim == 3

    if is_3d:
        depth, height, width = snapshots[0].shape
        if slice_z is None:
            slice_z = depth // 2
    else:
        height, width = snapshots[0].shape
        depth = 0

    fig, ax = plt.subplots(figsize=(6, 6 * height / max(width, 1)))
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()

    scatter_target = ax.scatter([], [], c="red", s=4, marker="s", alpha=0.5, label="target")
    scatter_drones = ax.scatter([], [], c="blue", s=drone_size, marker="o", label="drone")
    text_drones: list = []

    title_prefix = f"Z={slice_z} " if is_3d else ""
    time_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top",
                        fontfamily="monospace", fontsize=10)
    ax.legend(loc="upper right")

    frames_data = []
    for t in range(n_frames):
        snapshot = snapshots[t]
        positions = trajectory[t]

        if is_3d:
            # 提取 Z 切片
            z_slice = snapshot[slice_z, :, :]  # (H, W)
            ty, tx = np.where(z_slice)
            # 过滤靠近 slice_z 的无人机
            nearby = [(p[0], p[1]) for p in positions if abs(p[2] - slice_z) < 1.0]
        else:
            ty, tx = np.where(snapshot)
            nearby = [(p[0], p[1]) for p in positions]

        if nearby:
            xs, ys = zip(*nearby)
        else:
            xs, ys = [], []

        frames_data.append((tx, ty, xs, ys))

    def update(frame_idx):
        tx, ty, xs, ys = frames_data[frame_idx]

        scatter_target.set_offsets(np.column_stack([tx, ty]) if len(tx) > 0 else np.empty((0, 2)))
        scatter_drones.set_offsets(np.column_stack([xs, ys]) if len(xs) > 0 else np.empty((0, 2)))

        for txt in text_drones:
            txt.remove()
        text_drones.clear()
        for i, (x, y) in enumerate(zip(xs, ys)):
            txt = ax.annotate(str(i), (x, y), textcoords="offset points",
                              xytext=(5, 5), fontsize=6, color="navy")
            text_drones.append(txt)

        time_text.set_text(f"{title_prefix}t={frame_idx}")
        return [scatter_target, scatter_drones, time_text] + text_drones

    ani = animation.FuncAnimation(
        fig, update, frames=n_frames, interval=1000 // fps, blit=True
    )

    ani.save(output_path, writer="pillow", fps=fps)
    plt.close(fig)
    return output_path
