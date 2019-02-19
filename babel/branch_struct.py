class branch_struct:
    """
    A simple class to look what branches are traversed in the code
    """
    def __init__(self, size):
        """
        Initialize an array of correct size
        """
        self.m_size = size
        self.branches = [False]*size

    def add(self, m):
        if(m <= self.m_size):
            self.branches[m] = True
        else:
            raise Exception("List index out of range")

    def __str__(self):
        ret = ""
        for i in range(self.m_size):
            ret += str(i) + " = " + str(self.branches[i])
            ret += "\n"

        return ret
