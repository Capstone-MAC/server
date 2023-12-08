from datetime import datetime

class TimeUtility:
    @staticmethod
    def parse_time(input_time: str) -> str:
        time = datetime.strptime(input_time, "%Y/%m/%d %H:%M:%S")
        time_diff = (datetime.now() - time)
        seconds = time_diff.seconds
        days = time_diff.days
        if seconds < 60:
            return f"{seconds}초 전"
        
        elif seconds < 60 * 60:
            return f"{seconds // 60}분 전"
        
        elif days < 1:
            return f"{seconds // 60 // 60}시간 전"
        
        else:
            if days <= 3:
                return f"{days}일 전"
            
            else:
                return time.strftime("%Y년 %m월 %d일")