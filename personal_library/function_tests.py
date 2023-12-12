def add_numbers(number1: int, number2: int) -> int:
    """This function adds number1 and number2"""
    print(f"{number1} + {number2} is {number1+number2}")


def cheese_and_crackers(cheese_count, boxes_of_crackers):
    print(f"You have {cheese_count} cheeses!")
    print(f"You have {boxes_of_crackers} boxes of crackers!")
    print("Man that's enough for a party!")
    print("Get a blanket.\n")


amount_of_cheese = 10
amount_of_crackers = 50


cheese_and_crackers(cheese_count=amount_of_cheese, boxes_of_crackers=amount_of_crackers)
