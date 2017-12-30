using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows;
using System.Windows.Input;
using System.Threading;
using System.Windows.Forms;

namespace lsteam {
    public class MouseSimulator {
        [DllImport("User32.Dll")]
        public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern IntPtr FindWindowEx(IntPtr parentHandle, IntPtr childAfter, string className,
            string windowTitle);

        [DllImport("user32.dll", SetLastError = true)]
        static extern uint SendInput(uint nInputs, ref INPUT pInputs, int cbSize);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern IntPtr SendMessage(IntPtr hWnd, UInt32 msg, UInt32 wParam, IntPtr lParam);

        [StructLayout(LayoutKind.Sequential)]
        struct INPUT {
            public SendInputEventType type;
            public MouseKeybdhardwareInputUnion mkhi;
        }

        [StructLayout(LayoutKind.Explicit)]
        struct MouseKeybdhardwareInputUnion {
            [FieldOffset(0)] public MouseInputData mi;

            [FieldOffset(0)] public KEYBDINPUT ki;

            [FieldOffset(0)] public HARDWAREINPUT hi;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct KEYBDINPUT {
            public ushort wVk;
            public ushort wScan;
            public uint dwFlags;
            public uint time;
            public IntPtr dwExtraInfo;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct HARDWAREINPUT {
            public int uMsg;
            public short wParamL;
            public short wParamH;
        }

        struct MouseInputData {
            public int dx;
            public int dy;
            public uint mouseData;
            public MouseEventFlags dwFlags;
            public uint time;
            public IntPtr dwExtraInfo;
        }

        [Flags]
        enum MouseEventFlags : uint {
            MOUSEEVENTF_MOVE = 0x0001,
            MOUSEEVENTF_LEFTDOWN = 0x0002,
            MOUSEEVENTF_LEFTUP = 0x0004,
            MOUSEEVENTF_RIGHTDOWN = 0x0008,
            MOUSEEVENTF_RIGHTUP = 0x0010,
            MOUSEEVENTF_MIDDLEDOWN = 0x0020,
            MOUSEEVENTF_MIDDLEUP = 0x0040,
            MOUSEEVENTF_XDOWN = 0x0080,
            MOUSEEVENTF_XUP = 0x0100,
            MOUSEEVENTF_WHEEL = 0x0800,
            MOUSEEVENTF_VIRTUALDESK = 0x4000,
            MOUSEEVENTF_ABSOLUTE = 0x8000
        }

        [Flags]
        enum MessageEventFlags : UInt32 {
            WM_RBUTTONDBLCLK = 0x0206,
            WM_RBUTTONDOWN = 0x0204,
            WM_RBUTTONUP = 0x0205,
            WM_LBUTTONDBLCLK = 0x0203,
            WM_LBUTTONDOWN = 0x0201,
            WM_LBUTTONUP = 0x0202
        }

        enum SendInputEventType : int {
            InputMouse,
            InputKeyboard,
            InputHardware
        }

        public static void ClickLeftMouseButton(Point location) {
            INPUT mouseDownInput = new INPUT();
            mouseDownInput.type = SendInputEventType.InputMouse;
            mouseDownInput.mkhi.mi.dwFlags = MouseEventFlags.MOUSEEVENTF_LEFTDOWN;
            mouseDownInput.mkhi.mi.dx = location.X;
            mouseDownInput.mkhi.mi.dy = location.Y;
            SendInput(1, ref mouseDownInput, Marshal.SizeOf(new INPUT()));

            INPUT mouseUpInput = new INPUT();
            mouseUpInput.type = SendInputEventType.InputMouse;
            mouseUpInput.mkhi.mi.dwFlags = MouseEventFlags.MOUSEEVENTF_LEFTUP;
            mouseUpInput.mkhi.mi.dx = location.X;
            mouseUpInput.mkhi.mi.dy = location.Y;
            SendInput(1, ref mouseUpInput, Marshal.SizeOf(new INPUT()));
        }

        public static void ClickRightMouseButton(Point location) {
            INPUT mouseDownInput = new INPUT();
            mouseDownInput.type = SendInputEventType.InputMouse;
            mouseDownInput.mkhi.mi.dwFlags = MouseEventFlags.MOUSEEVENTF_RIGHTDOWN;
            mouseDownInput.mkhi.mi.dx = location.X;
            mouseDownInput.mkhi.mi.dy = location.Y;
            SendInput(1, ref mouseDownInput, Marshal.SizeOf(new INPUT()));

            INPUT mouseUpInput = new INPUT();
            mouseUpInput.type = SendInputEventType.InputMouse;
            mouseUpInput.mkhi.mi.dwFlags = MouseEventFlags.MOUSEEVENTF_RIGHTUP;
            mouseUpInput.mkhi.mi.dx = location.X;
            mouseUpInput.mkhi.mi.dy = location.Y;
            SendInput(1, ref mouseUpInput, Marshal.SizeOf(new INPUT()));
        }

        public static void FakeClickLeftButton(Point pt) {
            var wndHandle = FindWindow(null, "Yu-Gi-Oh! DUEL LINKS");
            if (wndHandle != IntPtr.Zero) {
                Console.WriteLine("Yes");
                //IntPtr handleWindow = FindWindowEx(wndHandle, IntPtr.Zero, "UnityWndClass", null);
                //if (handleWindow != IntPtr.Zero) {
                    //Console.WriteLine("Yes");
                    SendMessage(wndHandle, (UInt32) MessageEventFlags.WM_LBUTTONDOWN, 0,
                        (IntPtr) (((int)pt.X) & ((int)pt.Y) << 16));
                    //SendMessage(wndHandle, (UInt32) MessageEventFlags.WM_LBUTTONUP, 0,
                        //(IntPtr) (((int)pt.X) & ((int)pt.Y) << 16));
                //}
            }
        }
    }

    public class ClickOnPointTool {
        private const uint MOUSEEVENTF_MOVE = 0x0001;
        private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
        private const uint MOUSEEVENTF_LEFTUP = 0x0004;
        private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
        private const uint MOUSEEVENTF_RIGHTUP = 0x0010;

        private const uint MOUSEEVENTF_ABSOLUTE = 0x8000;

        [DllImport("User32.Dll")]
        public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("User32.Dll")]
        public static extern int GetClassName(int hwnd, StringBuilder lpClassName, int nMaxCount);

        [DllImport("User32.Dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        static extern bool SetCursorPos(uint x, uint y);

        [DllImport("user32.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.StdCall)]
        public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, UIntPtr dwExtraInfo);

        [DllImport("user32.dll")]
        static extern bool ClientToScreen(IntPtr hWnd, ref Point lpPoint);

        [DllImport("user32.dll")]
        internal static extern uint SendInput(uint nInputs, [MarshalAs(UnmanagedType.LPArray), In] INPUT[] pInputs,
            int cbSize);

        [DllImport("user32.dll")]
        static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        static extern IntPtr GetActiveWindow();
        
        enum SystemMetric
        {
            SM_CXSCREEN = 0,
            SM_CYSCREEN = 1,
        }

        [DllImport("user32.dll")]
        static extern int GetSystemMetrics(SystemMetric smIndex);

        static int CalculateAbsoluteCoordinateX(int x)
        {
            return (x * 65536) / GetSystemMetrics(SystemMetric.SM_CXSCREEN);
        }

        static int CalculateAbsoluteCoordinateY(int y)
        {
            return (y * 65536) / GetSystemMetrics(SystemMetric.SM_CYSCREEN);
        }

#pragma warning disable 649
        internal struct INPUT {
            public UInt32 Type;
            public MOUSEKEYBDHARDWAREINPUT Data;
        }

        [StructLayout(LayoutKind.Explicit)]
        internal struct MOUSEKEYBDHARDWAREINPUT {
            [FieldOffset(0)] public MOUSEINPUT Mouse;
        }

        internal struct MOUSEINPUT {
            public Int32 X;
            public Int32 Y;
            public UInt32 MouseData;
            public UInt32 Flags;
            public UInt32 Time;
            public IntPtr ExtraInfo;
        }

#pragma warning restore 649


        public static void ClickOnPoint(Point clientPoint) {
            var now = GetForegroundWindow();
            var wndHandle = FindWindow(null, "Yu-Gi-Oh! DUEL LINKS");
            /// get screen coordinates
            var oldPos = Cursor.Position;
            ClientToScreen(wndHandle, ref clientPoint);
            SetForegroundWindow(wndHandle);
            /// set cursor on coords, and press mouse
            //Cursor.Position = new Point(clientPoint.X, clientPoint.Y);
            var inputMouseMove = new INPUT();
            inputMouseMove.Type = 0; /// input type mouse
            inputMouseMove.Data.Mouse.Flags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;
            inputMouseMove.Data.Mouse.X = CalculateAbsoluteCoordinateX(clientPoint.X);
            inputMouseMove.Data.Mouse.Y = CalculateAbsoluteCoordinateY(clientPoint.Y);
            inputMouseMove.Data.Mouse.Time = 100;
            var inputMouseDown = new INPUT();
            inputMouseDown.Type = 0; /// input type mouse
            inputMouseDown.Data.Mouse.Flags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTDOWN;
            inputMouseDown.Data.Mouse.X = CalculateAbsoluteCoordinateX(clientPoint.X);
            inputMouseDown.Data.Mouse.Y = CalculateAbsoluteCoordinateY(clientPoint.Y);

            var inputMouseUp = new INPUT();
            inputMouseUp.Type = 0; /// input type mouse
            inputMouseUp.Data.Mouse.Flags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTUP;
            inputMouseDown.Data.Mouse.X = CalculateAbsoluteCoordinateX(clientPoint.X);
            inputMouseDown.Data.Mouse.Y = CalculateAbsoluteCoordinateY(clientPoint.Y);

            var inputs = new INPUT[] {inputMouseMove, inputMouseDown, inputMouseUp};
            SendInput((uint) inputs.Length, inputs, Marshal.SizeOf(typeof(INPUT)));
            Thread.Sleep(10);
            Cursor.Position = oldPos;
            SetForegroundWindow(now);
        }
    }

    public partial class steamgui {
        private const uint MOUSEEVENTF_MOVE = 0x0001;
        private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
        private const uint MOUSEEVENTF_LEFTUP = 0x0004;
        private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
        private const uint MOUSEEVENTF_RIGHTUP = 0x0010;

        private const uint MOUSEEVENTF_ABSOLUTE = 0x8000;

        private IntPtr handle = IntPtr.Zero;

        public static int return2() {
            return 2;
        }

        public steamgui() {
            setup();
        }

        [DllImport("User32.Dll")]
        public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("User32.Dll")]
        public static extern int GetClassName(int hwnd, StringBuilder lpClassName, int nMaxCount);

        [DllImport("User32.Dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        static extern bool SetCursorPos(uint x, uint y);

        [DllImport("user32.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.StdCall)]
        public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, UIntPtr dwExtraInfo);

        public void performClick(uint x, uint y) {
            SetCursorPos(x, y);
            mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTDOWN, x, y, 0, UIntPtr.Zero);
            Thread.Sleep(200);
            mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTUP, x, y, 0, UIntPtr.Zero);
        }

        private void moveToPos(uint x, uint y) {
            SetForegroundWindow(handle);
            mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, x, y, 0, UIntPtr.Zero);
        }

        private void setup() {
            var handle = FindWindow(null, "Yu-Gi-Oh! DUEL LINKS");


            if (handle == IntPtr.Zero) {
                Console.WriteLine("Handle Not Found");
                return;
            }
        }
    }
}