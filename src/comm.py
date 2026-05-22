"""
# 1. 功能
无人机通信网络模块。在通信半径内实现无人机间的消息广播与接收。
用于去中心化匹配时的声明协调。

# 2. 输入
- comm_radius: 通信半径（欧几里得距离内可达）
- drone_positions: 全体无人机位置映射 {drone_id: (x, y, z)}

# 3. 输出
- broadcast(): 向半径内所有其他无人机投递消息
- receive(): 取回该无人机的消息队列

# 4. 核心执行流程
1. 每轮更新全部无人机位置
2. 调用 broadcast(sender_id, msg) → 计算与所有其他无人机的距离
3. 距离 ≤ comm_radius 的目标收到消息入队
4. 调用 receive(drone_id) → 返回消息列表并清空队列

# 5. 依赖
- math（纯 Python，不依赖 numpy）
"""

import math


class CommNetwork:
    """通信网络：管理无人机之间的消息传递。"""

    def __init__(self, comm_radius: float = float("inf")):
        self.comm_radius = float(comm_radius)
        self._positions: dict[int, tuple[float, ...]] = {}
        self._inboxes: dict[int, list[dict]] = {}

    def update_positions(self, positions: dict[int, tuple[float, ...]]) -> None:
        """更新全体无人机的当前位置。

        Args:
            positions: {drone_id: (x, y, z)} 或 {drone_id: (x, y)}
        """
        self._positions = positions

    def broadcast(self, sender_id: int, msg_type: str, **payload) -> None:
        """向通信半径内的所有其他无人机广播消息。

        Args:
            sender_id: 发送方 ID
            msg_type: 消息类型字符串，如 "CLAIM", "RELEASE"
            **payload: 消息内容，如 target=(5, 5, 0)
        """
        sender_pos = self._positions.get(sender_id)
        if sender_pos is None:
            return

        msg = {"type": msg_type, "sender": sender_id, **payload}

        for drone_id, pos in self._positions.items():
            if drone_id == sender_id:
                continue
            dist = math.sqrt(sum((sp - op) ** 2 for sp, op in zip(sender_pos, pos)))
            if dist <= self.comm_radius + 1e-9:
                self._inboxes.setdefault(drone_id, []).append(msg)

    def receive(self, drone_id: int) -> list[dict]:
        """取回并清空指定无人机的消息队列。"""
        msgs = self._inboxes.pop(drone_id, [])
        return msgs

    def clear(self) -> None:
        """清空所有消息队列。"""
        self._inboxes.clear()
