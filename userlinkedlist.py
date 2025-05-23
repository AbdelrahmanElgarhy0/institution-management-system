import bcrypt

class Node:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password  # Store the hashed password
        self.role = role
        self.next = None  # Pointer to the next node

class UserLinkedList:
    def __init__(self):
        self.head = None

    def add_user(self, username, password, role):
        # Hash the password before adding it to the list
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        new_node = Node(username, hashed_password.decode(), role)

        # Add the new user at the start of the linked list
        if not self.head:
            self.head = new_node
        else:
            new_node.next = self.head
            self.head = new_node

    def find_user(self, username, password, role):
        current = self.head
        while current:
            if current.username == username and current.role == role:
                # Check the hashed password
                if bcrypt.checkpw(password.encode(), current.password.encode()):
                    return True  # Login successful
            current = current.next
        return False  # User not found or credentials invalid
