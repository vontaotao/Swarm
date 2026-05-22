"""
# 1. 功能
distributed_matcher.py 的单元测试。验证去中心化匹配的正确性和收敛性。

# 2. 输入
- 构造的快照、无人机、通信网络

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 测试空输入、简单分配、多无人机协商、3D 支持

# 5. 依赖
- pytest, numpy, src.distributed_matcher, src.drone, src.comm, src.grid
"""

import numpy as np
from src.drone import Drone
from src.comm import CommNetwork
from src.distributed_matcher import distributed_match
from src.grid import create_snapshot_rectangle, create_snapshot_sphere


def _all_drones_on_target(drones: list[Drone], snapshot: np.ndarray) -> bool:
    for d in drones:
        x, y, z = d.position
        ix, iy, iz = int(round(x)), int(round(y)), int(round(z))
        if snapshot.ndim == 2:
            if not (0 <= iy < snapshot.shape[0] and 0 <= ix < snapshot.shape[1]):
                return False
            if not snapshot[iy, ix]:
                return False
        else:
            if not (0 <= iz < snapshot.shape[0] and 0 <= iy < snapshot.shape[1] and 0 <= ix < snapshot.shape[2]):
                return False
            if not snapshot[iz, iy, ix]:
                return False
    return True


class TestDistributedMatch:
    def test_empty_drones(self):
        snapshot = np.ones((5, 5), dtype=bool)
        comm = CommNetwork(comm_radius=10.0)
        distributed_match(snapshot, [], comm)
        # 不应崩溃

    def test_one_drone_one_vacancy(self):
        snapshot = np.zeros((10, 10), dtype=bool)
        snapshot[5, 8] = True
        d = Drone(0, 0.0, 0.0)
        comm = CommNetwork(comm_radius=20.0)
        distributed_match(snapshot, [d], comm, max_rounds=20)
        assert _all_drones_on_target([d], snapshot)

    def test_two_drones_two_vacancies(self):
        snapshot = np.zeros((10, 10), dtype=bool)
        snapshot[0, 2] = True
        snapshot[0, 8] = True
        drones = [Drone(0, 2.0, 0.0), Drone(1, 8.0, 0.0)]
        comm = CommNetwork(comm_radius=20.0)
        distributed_match(snapshot, drones, comm, max_rounds=20)
        assert _all_drones_on_target(drones, snapshot)

    def test_more_drones_than_vacancies(self):
        snapshot = np.zeros((10, 10), dtype=bool)
        snapshot[3, 3] = True
        snapshot[3, 7] = True
        drones = [Drone(0, 0.0, 0.0), Drone(1, 0.0, 0.0), Drone(2, 0.0, 0.0)]
        comm = CommNetwork(comm_radius=20.0)
        distributed_match(snapshot, drones, comm, max_rounds=30)
        # 两架到目标，一架未分配在原位

    def test_limited_comm_range(self):
        """通信半径受限时，无人机只能看到邻居。"""
        snapshot = np.zeros((20, 20), dtype=bool)
        snapshot[5, 5] = True
        snapshot[5, 15] = True
        # drone_0 离目标近，drone_1 离得远且通信范围小
        drones = [Drone(0, 5.0, 4.0), Drone(1, 15.0, 0.0)]
        comm = CommNetwork(comm_radius=5.0)  # 两架无人机距离 14+ 无法通信
        distributed_match(snapshot, drones, comm, max_rounds=30)
        # 至少 drone 在自己的通信范围内能找到周边目标
        assert _all_drones_on_target(drones, snapshot)

    def test_3d_distributed(self):
        snapshot = create_snapshot_sphere(20, 20, 10, 10, 10, 5, 4)
        drones = [Drone(0, 0.0, 0.0, 0.0), Drone(1, 19.0, 19.0, 9.0)]
        comm = CommNetwork(comm_radius=30.0)
        distributed_match(snapshot, drones, comm, max_rounds=50)
        assert _all_drones_on_target(drones, snapshot)
