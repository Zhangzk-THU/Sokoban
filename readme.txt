文件组织：
report ---项目报告
game.py --- 游戏主体
test.py --- 实验，说明设计的两个启发函数之一不是可接受的
demo
其他 --- 建议不要修改

使用前：
conda create -n AIproject1 python=3.9
conda activate AIproject1
pip install -r requirements.txt
python game.py


使用时：
1.在终端输入：python game.py，显示：please enter level(0~6):
2.输入:0（选择第0关，也可以选0~6中其他关），显示please enter whether eggs are ordered(y/n):
3.输入:n（认为鸡蛋与洞口没有对应关系），正式开始游戏
4.游戏中：
（1）按上下左右键移动，按'D'回上一步，按'R'重启关卡，
（2）按'P'快速求解当前关，按'空格'严格求解当前关：求解后顺序显示解的各步，并在终端输出相关结果。
（3）若用AI求解：建议按"P"键使用不严格满足可接受性的启发函数快速求解；
若按"空格"键使用严格可接受的启发函数，基本需要一分钟以上时间，Pygame窗口显示"未响应"，请耐心等待。