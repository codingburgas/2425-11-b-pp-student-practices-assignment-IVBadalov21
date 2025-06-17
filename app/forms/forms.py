
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, FloatField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        from app.models import User
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        from app.models import User
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class SurveyForm(FlaskForm):
    """Survey form for collecting training data"""
    text_sample = TextAreaField('Text Sample', 
                               validators=[DataRequired(), Length(min=10, max=5000)],
                               render_kw={'placeholder': 'Enter text in your chosen language...',
                                        'rows': 5})
    language = SelectField('Language', 
                          choices=[
                              ('en', 'English'),
                              ('es', 'Spanish'),
                              ('fr', 'French'),
                              ('bg', 'Bulgarian'),
                              ('de', 'German')
                          ],
                          validators=[DataRequired()])
    confidence = FloatField('Confidence Level (0.0-1.0)', 
                           validators=[DataRequired(), NumberRange(min=0.0, max=1.0)],
                           default=1.0)
    submit = SubmitField('Submit Survey')

class PredictionForm(FlaskForm):
    """Form for language prediction"""
    input_text = TextAreaField('Text to Analyze', 
                              validators=[DataRequired(), Length(min=1, max=5000)],
                              render_kw={'placeholder': 'Enter text for language detection...',
                                       'rows': 6})
    make_public = BooleanField('Make this prediction public', default=False)
    submit = SubmitField('Detect Language')

class EditProfileForm(FlaskForm):
    """Form for editing user profile"""
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class EditUserForm(FlaskForm):
    """Admin form for editing user details"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    is_admin = BooleanField('Administrator')
    is_confirmed = BooleanField('Email Confirmed')
    submit = SubmitField('Update User')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')
