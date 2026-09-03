using Godot;

namespace MyGame.Godot.Scripts;

/// <summary>
/// 占位主菜单 —— 用于验证 C# 构建链与主场景加载。
/// 正式 UI 后续按 docs/ 设计稿替换。
/// </summary>
public partial class MainMenu : Control
{
    private void _OnQuitPressed()
    {
        GetTree().Quit();
    }
}
