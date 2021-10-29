from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,BooleanField,TextField,IntegerField,FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    usuario=StringField('Nombre de Usuario',validators=[DataRequired(message="Debes llenar este campo")])
    password=PasswordField('Contraseña',validators=[DataRequired(message="Debes llenar este campo")])
    recordar=BooleanField('Recordar usuario')

class RegistroForm(FlaskForm):
    NuevoUsuario=StringField('Nombre de Usuario',validators=[DataRequired(message="Debes llenar este campo")])
    NuevoPassword=PasswordField('Contraseña',validators=[DataRequired(message="Debes llenar este campo")])
    NuevoCorreo=TextField('Correo Electronico',validators=[DataRequired(message="Debes llenar este campo")])
    NuevoEdad=IntegerField('Edad',validators=[DataRequired(message="Debes llenar este campo")])

class PublicacionForm(FlaskForm):
    id = IntegerField('Código', validators=[DataRequired(message="Debes llenar este campo")])
    titulo = StringField('Titulo', validators=[DataRequired(message="Debes llenar este campo")])
    descripcion = StringField('Descripción', validators=[DataRequired(message="Debes llenar este campo")])
    imagen = FileField("Imagen")

class ComentarioForm(FlaskForm):
    id = IntegerField('id')
    usuario=StringField('usuario')
    comentario = StringField('comentario')

class imagenForm(FlaskForm):
    usuario=StringField('usuario')
    imagen = FileField("Imagen")