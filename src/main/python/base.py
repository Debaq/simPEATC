

"""

class ApplicationContext():
    
    def __init__(self) -> None:
        self.app = QApplication([])
    
    def get_resource(self, path):
        return f"resources/{path}"
       
        
context = ApplicationContext()
"""