"""
# 1. 功能
visualizer.py 的单元测试。验证 GIF 渲染不崩溃且输出文件有效。

# 2. 输入
- 构造的轨迹和快照数据

# 3. 输出
- pytest 测试结果

# 4. 核心执行流程
- 构造小规模仿真数据 → 调用 render_gif → 验证文件存在且非空

# 5. 依赖
- pytest, os, tempfile, src.visualizer, src.grid
"""

import os
import tempfile
import numpy as np
import pytest
from src.visualizer import render_gif
from src.grid import create_snapshot_rectangle, create_snapshot_sphere


class TestRenderGif:
    def setup_method(self):
        self._tmpfiles: list[str] = []

    def teardown_method(self):
        for path in self._tmpfiles:
            if os.path.exists(path):
                os.unlink(path)

    def _tmp_path(self, suffix: str = ".gif") -> str:
        path = tempfile.mktemp(suffix=suffix)
        self._tmpfiles.append(path)
        return path

    def test_render_simple_gif(self):
        """最小仿真渲染 GIF，验证文件生成。"""
        snapshot = create_snapshot_rectangle(20, 20, 10, 10, 6, 4)
        trajectory = [[(10.0, 10.0), (8.0, 10.0)]]

        out = self._tmp_path()
        result = render_gif([trajectory[0]], [snapshot], out, fps=5)
        assert result == out
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_render_multi_frame(self):
        """多帧渲染。"""
        snapshots = [
            create_snapshot_rectangle(30, 30, 10, 10, 5, 5),
            create_snapshot_rectangle(30, 30, 20, 20, 5, 5),
        ]
        trajectory = [[(10.0, 10.0), (8.0, 9.0)], [(20.0, 20.0), (22.0, 19.0)]]

        out = self._tmp_path()
        result = render_gif(trajectory, snapshots, out, fps=2)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            render_gif([], [], self._tmp_path())

    def test_3d_basic_rendering(self):
        """3D 快照 + 3D 轨迹生成 GIF。"""
        snapshot = create_snapshot_sphere(20, 20, 10, 10, 10, 5, 5)
        trajectory = [[(10.0, 10.0, 5.0), (8.0, 12.0, 4.0)]]
        out = self._tmp_path()
        result = render_gif(trajectory, [snapshot], out, fps=5)
        assert result == out
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_slice_z_out_of_bounds_raises(self):
        """slice_z 越界抛出 ValueError。"""
        snapshot = create_snapshot_sphere(20, 20, 10, 10, 10, 5, 5)
        trajectory = [[(10.0, 10.0, 5.0)]]
        with pytest.raises(ValueError):
            render_gif(trajectory, [snapshot], self._tmp_path(), slice_z=99)
