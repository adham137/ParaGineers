class Logger:
    """Simple logger class with color support."""

    # ANSI escape codes for colors
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @staticmethod
    def _log(message: str, color: str, agent_name: str):
        print(f"{color}[{agent_name}] {message}{Logger.RESET}")

    @staticmethod
    def info(message: str, agent_name: str, color_code: str = WHITE):
        Logger._log(message, color_code, agent_name)

    @staticmethod
    def success(message: str, agent_name: str):
        Logger._log(message, Logger.GREEN, agent_name)

    @staticmethod
    def warning(message: str, agent_name: str):
        Logger._log(message, Logger.YELLOW, agent_name)

    @staticmethod
    def error(message: str, agent_name: str):
        Logger._log(message, Logger.RED, agent_name)

    @staticmethod
    def debug(message: str, agent_name: str, color_code: str = MAGENTA):
        # Dedicated color for debug, or use a specific one if needed
        Logger._log(f"DEBUG: {message}", color_code, agent_name)

# Define color constants for each module/agent
class LogColors:
    ORCHESTRATOR = Logger.CYAN
    OMP_EXPERT = Logger.BLUE
    MPI_EXPERT = Logger.MAGENTA
    CHECKER = Logger.YELLOW
    GROQ_CLIENT = Logger.GREEN
    MAIN = Logger.WHITE