import os
from flask.helpers import flash
from werkzeug.utils import secure_filename
from forms.forms import *
from flask import Flask, render_template, url_for, redirect, jsonify,request,session
from db import *
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = os.path.abspath("static/imagenes/imgpub")
UPLOAD_FOLDER2 = os.path.abspath("static/imgperfil")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["UPLOAD_FOLDER2"] = UPLOAD_FOLDER2

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET', 'POST'])
def index():
    if 'user' in session:
        form = PublicacionForm()
        if request.method == 'POST':
            titulo = request.form['titulo']
            descripcion = request.form['descripcion']
            imagen = request.files['imagen']
            usuario = session['user']
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            
            db = get_db()
            db.execute('INSERT INTO publicacion (titulo, descripcion, url, usuario) VALUES (?,?,?,?)', (titulo, descripcion,filename,usuario))
            db.commit()

            return redirect(url_for("index"))
        db=get_db()
        cursorObj = db.cursor()
        cursorObj.execute("SELECT * FROM publicacion")
        publicacion = cursorObj.fetchall()

        usuario=session ['user']
        db= get_db()
        cursorObj2 = db.cursor()
        sql = f'SELECT * FROM User WHERE usuario = "{usuario}"'
        cursorObj2.execute(sql)
        usuarios = cursorObj2.fetchall()

        return render_template('index.html',form=form,publicacion=publicacion,usuarios=usuarios)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    if(form.validate_on_submit()):
        usuario = form.usuario.data
        contraseña = form.password.data
        sql = f'SELECT * FROM User WHERE usuario = "{usuario}"'
        db = get_db()
        cursorObj = db.cursor()
        cursorObj.execute(sql)
        usuarios = cursorObj.fetchall()  
    
        if len(usuarios) > 0:
            contraseñaHash = usuarios[0][2]
            print("si encontro usuario")
            if check_password_hash(contraseñaHash, contraseña):
                session.clear()
                session['id'] = usuarios[0][0]
                session['user'] = usuarios[0][1]
                session['password'] = contraseñaHash
                session['rol'] = usuarios[0][5] 
                print('estoy dentro')
                return redirect(url_for('index'))              
            else:
                print('incorrecto')
                flash('Clave incorrecta')
                return redirect(url_for('login'))           
        else:
            flash('El usuario ingresado no existe') 
            return redirect(url_for('login'))            
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if request.method == 'POST':
        usuario = request.form['NuevoUsuario']
        contraseña = request.form['NuevoPassword']
        correo = request.form['NuevoCorreo']
        edad = request.form['NuevoEdad']
        contraseñaHash = generate_password_hash(contraseña)
        sql = 'INSERT INTO user (usuario, contraseña ,correo ,edad , rol) VALUES (?, ?, ?, ?, ?)' 
        sql2 = 'INSERT INTO imgperfil (usuario, url) VALUES (?, ?)' 
        db = get_db()
        result = db.execute(sql,(usuario,contraseñaHash,correo,edad, 2)).rowcount
        db.commit()
        db.execute(sql2,(usuario,'incognito.png'))
        db.commit()
        if result !=0:
            flash('Registro  extitoso')
            return redirect(url_for('login'))
        else:
            flash('woops! Hubo un error. Intenta nuevamente')            
    return render_template('registro.html', form=form)

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user' in session:
        db=get_db()
        cursorObj = db.cursor()
        cursorObj.execute("SELECT * FROM publicacion")
        publicacion = cursorObj.fetchall()
        print(publicacion)
        return render_template('perfil.html',publicacion=publicacion)
    else:
        return redirect(url_for('login')) 

@app.route('/detalle', methods=['GET', 'POST'])
def detalle():
    if 'user' in session:
        form=ComentarioForm()
        
        if request.method == 'POST':
            id = request.form['detalle']
            print('este es el id: ',id)
            sql = f'SELECT * FROM publicacion WHERE id = "{id}"'
            db = get_db()
            cursorObj = db.cursor()
            cursorObj.execute(sql)
            publicacion = cursorObj.fetchall()


            sql2=f'SELECT * FROM Comentarios WHERE id = "{id}"'
            cursorObj2=db.cursor()
            cursorObj2.execute(sql2)
            Comentarios = cursorObj2.fetchall()


            db = get_db()
            cursorObj3 = db.cursor()
            cursorObj3.execute("SELECT * FROM imgperfil")
            imagenes = cursorObj3.fetchall()
            print("aqui esta mi imagen de perfil",imagenes)
            return render_template('detalle.html',publicacion=publicacion,form=form,Comentarios=Comentarios,imagenes=imagenes)
        
        
        if request.method == 'GET':

            id= request.args.get('id')
            print('este es el id: ',id)
            sql = f'SELECT * FROM publicacion WHERE id = "{id}"'
            db = get_db()
            cursorObj = db.cursor()
            cursorObj.execute(sql)
            publicacion = cursorObj.fetchall()
            print(publicacion)

            sql2=f'SELECT * FROM Comentarios WHERE id = "{id}"'
            cursorObj2=db.cursor()
            cursorObj2.execute(sql2)
            Comentarios = cursorObj2.fetchall()
            print(Comentarios)

            
            cursorObj3 = db.cursor()
            cursorObj3.execute("SELECT * FROM imgperfil")
            imagenes = cursorObj3.fetchall()
            print("aqui esta mi imagen de perfil",imagenes)
            return render_template('detalle.html',publicacion=publicacion,form=form,Comentarios=Comentarios,imagenes=imagenes)
    else:
        return redirect(url_for('login'))    
    

@app.route('/comentar',methods=['GET', 'POST'])
def comentar():

    if request.method == 'POST':
        id = request.form['id']
        usuario = session['user']
        comentario = request.form['comentario']
        
        sql = 'INSERT INTO Comentarios (id, usuario ,comentario) VALUES (?, ?, ?)' 
        db = get_db()
        db.execute(sql,(id,usuario,comentario)).rowcount
        db.commit()
        return redirect(url_for('detalle',id=id))
    return redirect(url_for('detalle'))



@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    if 'user' in session:
        if request.method == 'POST':
            titulo = request.form['buscar']
            sql = f'SELECT * FROM publicacion WHERE titulo LIKE "%{titulo}%"'
            db = get_db()
            cursorObj = db.cursor()
            cursorObj.execute(sql)
            publicacion = cursorObj.fetchall()
            print(publicacion)
            return render_template('busqueda.html',publicacion=publicacion)
    else:
        return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session:
        usuario = session['user'] 
    
        return render_template('dashboard.html')
    
    else:
        return redirect(url_for('login'))

@app.route('/imgperfil', methods=['GET', 'POST'])
def imgperfil():
    
    if 'user' in session:
        usuario = session['user']   
        
        if request.method == 'GET':
            form = imagenForm()        
            sql = f'SELECT * FROM imgperfil WHERE usuario LIKE "%{usuario}%"'
            db = get_db()
            cursorObj = db.cursor()
            cursorObj.execute(sql)
            Imagen = cursorObj.fetchall()[0]
            print("este es el usuario en sesion:",usuario)
            return render_template('imgperfil.html', form=form, Imagen = Imagen)
        if request.method == 'POST':
            usuario = request.form['usuario']
            imagen = request.files['imagen']
            if imagen.filename !="":
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config["UPLOAD_FOLDER2"], filename))
                
            else:
                filename = request.form['filename']        
            db = get_db()
            sql = 'UPDATE imgperfil SET  url = ? WHERE usuario = ? '
            result = db.execute(sql,(filename,usuario)).rowcount
            db.commit()
            
            if result > 0:
                flash('Registro editado correctamente')
            else:
                flash('No se pudo editar el registro')             
            return redirect(url_for('imgperfil'))
    else:
        return redirect(url_for('login'))

@app.route('/Gusuario', methods=['GET', 'POST'])
def Gusuario():
    if 'user' in session:
 
        if request.method == 'POST':
            id = request.form['borrar']
            sql = 'DELETE FROM Publicacion WHERE usuario = ?'
            sql2='DELETE FROM Comentarios WHERE usuario = ?'
            sql3='DELETE FROM imgperfil WHERE usuario = ?'
            sql4='DELETE FROM User WHERE usuario = ?'
            db = get_db()
            result = db.execute(sql, [id]).rowcount
            db.execute(sql2, [id]).rowcount
            db.execute(sql3, [id]).rowcount
            db.execute(sql4, [id]).rowcount
            if result > 0:
                flash('Producto eliminado exitosamente')
            else:
                flash('No se pudo eliminar el producto')        
            db.commit()
            db.close()    
            return redirect(url_for('Gusuario'))

        db=get_db()
        cursorObj = db.cursor()
        cursorObj.execute("SELECT * FROM User")
        Usuarios = cursorObj.fetchall()

        db=get_db()
        cursorObj2 = db.cursor()
        cursorObj2.execute("SELECT * FROM imgperfil")
        imagenes = cursorObj2.fetchall()

        db=get_db()
        cursorObj3 = db.cursor()
        cursorObj3.execute("SELECT * FROM Publicacion")
        publicacion = cursorObj3.fetchall()


        return render_template('Gusuario.html',Usuarios=Usuarios,imagenes=imagenes,publicacion=publicacion)
    else:
        return redirect(url_for('login'))

@app.route('/Gimagenes', methods=['GET', 'POST'])
def Gimagenes():
    if 'user' in session:
        usuario = session['user']  
        if request.method == 'POST':
            id = request.form['borrar']
            sql = 'DELETE FROM Publicacion WHERE id = ?'
            sql2='DELETE FROM Comentarios WHERE id = ?'
            db = get_db()
            result = db.execute(sql, id).rowcount
            db.execute(sql2, id).rowcount
            if result > 0:
                flash('Producto eliminado exitosamente')
            else:
                flash('No se pudo eliminar el producto')        
            db.commit()
            db.close()    
            return redirect(url_for('Gimagenes'))

        db=get_db()
        cursorObj = db.cursor()
        cursorObj.execute("SELECT * FROM publicacion")
        publicaciones = cursorObj.fetchall()


        return render_template('Gimagenes.html',publicaciones=publicaciones)
    else:
        return redirect(url_for('login'))

@app.route('/Gcomentarios', methods=['GET', 'POST'])
def Gcomentarios():
    if 'user' in session:
        usuario = session['user']  
        if request.method == 'POST':
            id = request.form['borrar']
            print("este es el id:",id)
            sql = 'DELETE FROM Comentarios WHERE comentario = ?'
            db = get_db()
            result = db.execute(sql, [id]).rowcount
            print("este es el resultado:",result )

            if result > 0:
                flash('Producto eliminado exitosamente')
            else:
                flash('No se pudo eliminar el producto')        
            db.commit()
            db.close()    
            return redirect(url_for('Gcomentarios'))

        db=get_db()
        cursorObj = db.cursor()
        cursorObj.execute("SELECT * FROM Comentarios")
        Comentarios = cursorObj.fetchall()
        db = get_db()
        cursorObj2 = db.cursor()
        cursorObj2.execute("SELECT * FROM imgperfil")
        imagenes = cursorObj2.fetchall()
        print("estos son los comentarios:",Comentarios)
        print(Comentarios[1])


        return render_template('Gcomentarios.html',Comentarios=Comentarios,imagenes=imagenes)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)