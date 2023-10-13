using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Proyecto2
{
    public partial class Login : Form
    {
        public string Cedula { get { return txtUsuario.Text; } }


        public Login()
        {
            InitializeComponent();
        }
        public string ObtenerCedula()
        {
            return txtUsuario.Text;
        }

        private void lblregistro_Click(object sender, EventArgs e)
        {
            // Oculta el formulario de inicio de sesión
            this.Hide();

            // Crear una instancia del formulario de registro
            Registro registroForm = new Registro();

            // Mostrar el formulario de registro
            registroForm.Show();
        }

        private void Login_Load(object sender, EventArgs e)
        {
            timer1.Start();
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            lblTime.Text = DateTime.Now.ToString("HH:mm:ss");
        }

        private void btnSesion_Click(object sender, EventArgs e)
        {
            // Obtener el número de cédula y la contraseña ingresados por el usuario
            string cedulaLogin = ObtenerCedula();
            string contrasena = txtContrasena.Text;

            try
            {
                // Establecer una conexión con el servidor
                using (TcpClient client = new TcpClient("localhost", 8888))
                {
                    // Crear un stream de escritura para enviar la solicitud al servidor
                    using (NetworkStream stream = client.GetStream())
                    {
                        // Construir la solicitud en el formato adecuado
                        string solicitud = $"LOGIN {cedulaLogin} & {contrasena}";
                        byte[] solicitudBytes = Encoding.ASCII.GetBytes(solicitud);

                        // Enviar la solicitud al servidor
                        stream.Write(solicitudBytes, 0, solicitudBytes.Length);

                        // Crear un buffer para recibir la respuesta del servidor
                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);

                        // Decodificar la respuesta del servidor
                        string respuesta = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                        // Verificar la respuesta del servidor
                        if (respuesta.Trim() == "Inicio de sesion exitoso")
                        {
                            MessageBox.Show("Inicio de sesion exitoso.");
                            Inicio inicio = new Inicio(cedulaLogin);
                            inicio.Show();
                            this.Hide();
                        }
                        else if (respuesta.Trim() == "Cedula o contrasena incorrecta")
                        {
                            MessageBox.Show("Error: Cedula o contraseña incorrecta.");
                        }
                        else
                        {
                            MessageBox.Show("Error desconocido.");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error de conexión: " + ex.Message);
            }

        }
    }
}
