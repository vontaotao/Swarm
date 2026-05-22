"""
# 1. 功能
comm.py 的单元测试。验证消息广播、接收和通信半径限制。

# 2. 输入
- 构造的无人机位置和消息

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试单播、多发、通信半径限制、队列清空

# 5. 依赖
- pytest, src.comm
"""

from src.comm import CommNetwork


class TestCommNetwork:
    def test_broadcast_and_receive(self):
        net = CommNetwork(comm_radius=10.0)
        net.update_positions({0: (0.0, 0.0, 0.0), 1: (3.0, 4.0, 0.0)})  # 距离 5
        net.broadcast(0, "CLAIM", target=(5, 5, 0))
        msgs = net.receive(1)
        assert len(msgs) == 1
        assert msgs[0]["type"] == "CLAIM"
        assert msgs[0]["sender"] == 0
        assert msgs[0]["target"] == (5, 5, 0)

    def test_out_of_range_no_receive(self):
        net = CommNetwork(comm_radius=3.0)
        net.update_positions({0: (0.0, 0.0, 0.0), 1: (3.0, 4.0, 0.0)})  # 距离 5 > 3
        net.broadcast(0, "CLAIM", target=(0, 0, 0))
        msgs = net.receive(1)
        assert len(msgs) == 0

    def test_sender_does_not_receive_own_message(self):
        net = CommNetwork(comm_radius=10.0)
        net.update_positions({0: (0.0, 0.0, 0.0)})
        net.broadcast(0, "CLAIM", target=(1, 1, 1))
        msgs = net.receive(0)
        assert len(msgs) == 0

    def test_multiple_receivers(self):
        net = CommNetwork(comm_radius=10.0)
        net.update_positions({0: (0.0, 0.0, 0.0), 1: (1.0, 0.0, 0.0), 2: (2.0, 0.0, 0.0)})
        net.broadcast(0, "CLAIM", target=(5, 0, 0))
        assert len(net.receive(1)) == 1
        assert len(net.receive(2)) == 1

    def test_receive_clears_queue(self):
        net = CommNetwork(comm_radius=10.0)
        net.update_positions({0: (0.0, 0.0, 0.0), 1: (1.0, 0.0, 0.0)})
        net.broadcast(0, "CLAIM", target=(5, 0, 0))
        assert len(net.receive(1)) == 1
        assert len(net.receive(1)) == 0  # 已清空

    def test_2d_positions(self):
        """2D 位置（无 z）也能正常工作。"""
        net = CommNetwork(comm_radius=5.0)
        net.update_positions({0: (0.0, 0.0), 1: (3.0, 4.0)})
        net.broadcast(0, "HELLO")
        msgs = net.receive(1)
        assert len(msgs) == 1

    def test_clear(self):
        net = CommNetwork(comm_radius=10.0)
        net.update_positions({0: (0.0, 0.0, 0.0), 1: (1.0, 0.0, 0.0)})
        net.broadcast(0, "CLAIM")
        net.clear()
        assert len(net.receive(1)) == 0
