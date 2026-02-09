# Conditionals in Python
# if - elif - else loops
temp = 15
if temp > 20:
    print("Its hotter than expected")
elif temp > 10 and temp <= 20: # or 10<temp<=20
    print("Its normal")
else:
    print("Its cold")

# try-except blocks

try:
    print("6"/2)
except Exception as e:
    print("The error is: ", e)