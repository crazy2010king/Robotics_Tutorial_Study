# 先安装:  pip install drake   (或在 Deepnote 里已预装)
import numpy as np
from pydrake.systems.framework import LeafSystem
from pydrake.systems.analysis import Simulator

# 用 Drake 写一个"单摆"系统: 状态 x=[角度θ, 角速度θdot]
class SimplePendulum(LeafSystem):
    def __init__(self):
        LeafSystem.__init__(self)
        state_index = self.DeclareContinuousState(2)          # 2个连续状态
        self.DeclareStateOutputPort("state", state_index)     # 暴露一个输出端口

    def DoCalcTimeDerivatives(self, context, derivatives):
        x = context.get_continuous_state_vector().CopyToVector()
        theta, thetadot = x[0], x[1]
        g, l = 9.81, 1.0
        thetaddot = -(g / l) * np.sin(theta)                  # 单摆动力学 θddot=-(g/l)sinθ
        derivatives.get_mutable_vector().SetFromVector([thetadot, thetaddot])

system = SimplePendulum()
simulator = Simulator(system)
context = simulator.get_mutable_context()
context.SetContinuousState([np.pi - 0.1, 0.0])   # 从"几乎直立"释放(不稳定平衡点附近)
simulator.Initialize()
simulator.AdvanceTo(5.0)                          # 仿真 5 秒
print("5秒后状态 [θ, θdot] =",
      np.round(context.get_continuous_state_vector().CopyToVector(), 3))
print("(θ≈π 是不稳定平衡, 它会倒下去并来回摆动)")