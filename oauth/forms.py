# class AdminLogin:
#     email = EmailField(validators=[DataRequired()])
#     password = PasswordField(validators=[DataRequired()])
#
#     def validate_password(self, field):
#         email = self.email.data.lower()
#         user = User.query.filter_by(email=email).first()
#         if not user or not user.check_password(field.data):
#             raise StopValidation('Email or password is invalid.')
#
#         if self.confirm.data:
#             login(user, False)