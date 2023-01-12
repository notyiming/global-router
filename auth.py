import pyrebase



email = "ymtan.2062@gmail.com"
password = "123456"
# user = auth.create_user_with_email_and_password(email, password)
# print(user)
user= auth.sign_in_with_email_and_password(email, password)
print(auth.get_account_info(user["idToken"]))

auth.send_email_verification(user["idToken"])
auth.send_password_reset_email(email)