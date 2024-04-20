class MyClass:
    def __init__(self, name):
        self.my_array = []  # Khai báo một thuộc tính mảng rỗng
        self.name = name

    def add_element(self, element):
        self.my_array.append(element)  # Thêm phần tử vào mảng

    def get_length(self):
        return len(self.my_array)  # Trả về độ dài của mảng


def a(Input):
    # Input.my_array.append(1)
    print("askjd")

x = MyClass("hi")
a(x)
print(len(x.my_array))