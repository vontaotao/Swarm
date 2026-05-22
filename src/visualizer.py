"""
# 1. 功能
matplotlib 可视化模块。将仿真轨迹和快照序列渲染为 GIF 动画。

# 2. 输入
- trajectory: list[list[(x, y)]] — 每个时间步的无人机位置
- snapshots: list[np.ndarray] — 对应目标快照
- output_path: 输出文件路径
- fps: 帧率

# 3. 输出
- GIF 文件保存到 output_path
- 返回文件路径字符串

# 4. 核心执行流程
1. 逐帧绘制：灰色网格 → 红色目标像素 → 蓝色无人机点（含编号）
2. 使用 matplotlib.animation 合成 GIF
3. 保存到磁盘

# 5. 依赖
- numpy, matplotlib, PIL (Pillow)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # 无 GUI 后端
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def render_gif(
    trajectory: list[list[tuple[float, float]]],
    snapshots: list[np.ndarray],
    output_path: str = "swarm.gif",
    fps: int = 5,
    drone_size: int = 60,
) -> str:
    """将仿真轨迹渲染为 GIF 动画。

    Args:
        trajectory: trajectory[t][i] = 第 t 步第 i 架无人机的 (x, y)
        snapshots: 对应每个时间步的快照网格
        output_path: 输出 GIF 文件路径
        fps: 每秒帧数
        drone_size: 图中无人机点的大小

    Returns:
        输出文件路径
    """
    if not trajectory or not snapshots:
        raise ValueError("trajectory 和 snapshots 不能为空")

    n_frames = len(trajectory)
    height, width = snapshots[0].shape

    fig, ax = plt.subplots(figsize=(6, 6 * height / max(width, 1)))
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()

    # 静态：网格
    scatter_target = ax.scatter([], [], c="red", s=4, marker="s", alpha=0.5, label="target")
    scatter_drones = ax.scatter([], [], c="blue", s=drone_size, marker="o", label="drone")
    text_drones = []  # 编号标签

    time_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top",
                        fontfamily="monospace", fontsize=10)
    ax.legend(loc="upper right")

    # 预计算每帧的绘制数据
    frames_data = []
    for t in range(n_frames):
        snapshot = snapshots[t]
        positions = trajectory[t]

        # 目标像素坐标
        ty, tx = np.where(snapshot)
        # 无人机位置
        if positions:
            xs, ys = zip(*positions)
        else:
            xs, ys = [], []

        frames_data.append((tx, ty, xs, ys))

    def update(frame_idx):
        tx, ty, xs, ys = frames_data[frame_idx]

        # 更新目标点
        scatter_target.set_offsets(np.column_stack([tx, ty]))

        # 更新无人机点
        scatter_drones.set_offsets(np.column_stack([xs, ys]))

        # 清除旧编号，画新编号
        for txt in text_drones:
            txt.remove()
        text_drones.clear()
        for i, (x, y) in enumerate(zip(xs, ys)):
            txt = ax.annotate(str(i), (x, y), textcoords="offset points",
                              xytext=(5, 5), fontsize=6, color="navy")
            text_drones.append(txt)

        time_text.set_text(f"t={frame_idx}")

        artist_list = [scatter_target, scatter_drones, time_text] + text_drones
        return artist_list

    ani = animation.FuncAnimation(
        fig, update, frames=n_frames, interval=1000 // fps, blit=True
    )

    ani.save(output_path, writer="pillow", fps=fps)
    plt.close(fig)
    return output_path
