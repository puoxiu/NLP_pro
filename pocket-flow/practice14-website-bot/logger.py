class ColoredLogger:
    """带颜色的日志输出工具类，支持不同级别日志的彩色显示"""
    
    # ANSI 转义码 - 文本颜色
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # ANSI 转义码 - 重置
    RESET = "\033[0m"
    
    @classmethod
    def error(cls, message):
        print(f"{cls.RED}[ERROR] {message}{cls.RESET}")
    
    @classmethod
    def warning(cls, message):
        print(f"{cls.YELLOW}[WARNING] {message}{cls.RESET}")
    
    @classmethod
    def info(cls, message):
        print(f"{cls.CYAN}[INFO] {message}{cls.RESET}")
    
    @classmethod
    def success(cls, message):
        print(f"{cls.CYAN}[SUCCESS] {message}{cls.RESET}")
    
    @classmethod
    def debug(cls, message):
        print(f"{cls.CYAN}[DEBUG] {message}{cls.RESET}")


if __name__ == "__main__":
    ColoredLogger.error("文件不存在")
    ColoredLogger.warning("磁盘空间不足")
    ColoredLogger.info("程序启动成功")
    ColoredLogger.success("数据处理完成")
    ColoredLogger.debug("进入循环体")
    