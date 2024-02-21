def evaluate_loan(credit_score, age, income, criminal_record, employed):
    if credit_score < 600:
        return "Loan Denied: Low credit score"
    if age < 18 or age > 65:
        return "Loan Denied: Age criteria not met"
    if income < 20000:
        return "Loan Denied: Insufficient income"
    if criminal_record:
        return "Loan Denied: Criminal record found"
    if not employed:
        return "Loan Denied: Unemployed"
    return "Loan Approved"


def is_failed(student_id, grade):
    grade_scale = {
        'A+': 4.0,
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'C-': 1.7,
        'D+': 1.3,
        'D': 1.0,
        'F': 0.0
    }
    
    A_plus = "A+"
    A = "A"
    A_minus = "A-"
    B_plus = "B+"
    B = "B"
    B_minus = "B-"
    C_plus = "C+"
    C = "C"
    C_minus = "C-"
    D_plus = "D+"
    D = "D"

    if grade >= 95:
        return A_plus
    if grade >= 90 and grade < 95:
        return A
    if grade >= 85 and grade < 90:
        return A_minus
    if grade >= 80 and grade < 85:
        return B_plus
    if grade >= 75 and grade < 80:
        return B
    if grade >= 70 and grade < 75:
        return B_minus
    if grade >= 65 and grade < 70:
        return C_plus
    if grade >= 60 and grade < 65:
        return C
    if grade >= 55 and grade < 60:
        return C_minus
    if grade >= 50 and grade < 55:
        return D_plus
    if grade >= 45 and grade < 50:
        return D

    if grade in grade_scale:
        if grade_scale[grade] < 2.0:
            return f"Student ID: {student_id}, Grade: {grade}, Result: Failed"
        else:
            return f"Student ID: {student_id}, Grade: {grade}, Result: Passed"
        
    return f"Student ID: {student_id}, Grade: {grade}, Result: Invalid Grade"

def sample(a, b):
    return a + b

def calculate_area(radius):
    """
    Calculate the area of a circle given its radius.
    """
    pi = 3.14159
    area = pi * radius * radius
    return area

def calculate_volume(radius):
    """
    Calculate the volume of a sphere given its radius.
    """
    pi = 3.14159
    volume = (4 / 3) * pi * radius * radius * radius
    return volume
    
        


if __name__ == "__main__":
    # # Test evaluate_loan method
    credit_score = 700
    age = 30
    income = 35000
    criminal_record = False
    employed = True
    loan_status = evaluate_loan(credit_score, age, income, criminal_record, employed)
    print(loan_status)
    
    # Test is_failed method
    student_id = "123456"
    grade = "B-"
    result = is_failed(student_id, grade)
    print(result)