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
    public partial class Registro : Form
    {
        public Registro()
        {
            InitializeComponent();
        }

        private void pictureBox3_Click(object sender, EventArgs e)
        {
            // Oculta el formulario de inicio de sesión
            this.Hide();

            // Crear una instancia del formulario de registro
            Login registroForm = new Login();

            // Mostrar el formulario de registro
            registroForm.Show();
        }

        private void BtnSolicitud_Click(object sender, EventArgs e)
        {

            // Obtener los datos ingresados por el usuario
            string cedula = txtCedula.Text;
            string nombre = txtNombre.Text;
            string apellido1 = txtApellido.Text;
            string apellido2 = txtSapellido.Text;
            string telefono = txtTelefono.Text;
            string correo = txtCorreo.Text;
            string direccion = txtDireccion.Text;
            string contrasena = txtContraseña.Text;

            try
            {
                // Establecer una conexión con el servidor
                using (TcpClient client = new TcpClient("localhost", 8888))
                {
                    // Crear un stream de escritura para enviar la solicitud al servidor
                    using (NetworkStream stream = client.GetStream())
                    {
                        // Construir la solicitud en el formato adecuado
                        string solicitud = $"REGISTRO {cedula}&{nombre}&{apellido1}&{apellido2}&{telefono}&{correo}&{direccion}&{contrasena}";
                        byte[] solicitudBytes = Encoding.UTF8.GetBytes(solicitud);


                        // Enviar la solicitud al servidor
                        stream.Write(solicitudBytes, 0, solicitudBytes.Length);

                        // Crear un buffer para recibir la respuesta del servidor
                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);

                        // Decodificar la respuesta del servidor
                        string respuesta = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                        // Verificar la respuesta del servidor
                        if (respuesta.Trim().ToLower() == "registro exitoso")
                        {
                            MessageBox.Show("Registro exitoso. Se ha guardado su información.");
                        }
                        else
                        {
                            MessageBox.Show("Error al registrar los datos.");
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
