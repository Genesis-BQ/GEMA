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
using System.Xml;

namespace Proyecto2
{
    public partial class Inicio : Form
    {
        private string cedulaInicio;
        private TcpClient cliente;

        public Inicio(string cedula)
        {
            InitializeComponent();
            cedulaInicio = cedula;
            
        }


        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }

        private void btnConsultar_Click(object sender, EventArgs e)
        {

        }

        private void btnModificar_Click(object sender, EventArgs e)
        {
            // Obtén los nuevos datos del formulario
            string nuevaCedula = txtCedula.Text;
            string nuevoNombre = txtNombre.Text;
            string nuevoApellido = txtApellido.Text;
            string nuevoSapellido = txtSapellido.Text;
            string nuevoTelefono = txtTelefono.Text;
            string nuevoCorreo = txtCorreo.Text;
            string nuevaDireccion = txtDireccion.Text;
            string nuevaContrasena = txtContraseña.Text;

            // Establece una conexión con el servidor
            cliente = new TcpClient();
            cliente.Connect("localhost", 8888);  // Cambia "localhost" y el puerto según corresponda

            // Envía una solicitud de modificación al servidor
            string solicitudModificacion = $"MODIFICACION {nuevaCedula}&{nuevoNombre}&{nuevoApellido}&{nuevoSapellido}&{nuevoTelefono}&{nuevoCorreo}&{nuevaDireccion}&{nuevaContrasena}";
            byte[] solicitudBytes = Encoding.UTF8.GetBytes(solicitudModificacion);
            cliente.GetStream().Write(solicitudBytes, 0, solicitudBytes.Length);

            // Espera la respuesta del servidor
            byte[] buffer = new byte[1024];
            int bytesRead = cliente.GetStream().Read(buffer, 0, buffer.Length);
            string respuesta = Encoding.UTF8.GetString(buffer, 0, bytesRead);

            // Procesa la respuesta del servidor (puede ser un mensaje de éxito o error)
            MessageBox.Show(respuesta);

            // Cierra la conexión con el servidor
            cliente.Close();

        }

        private void btnBorrar_Click(object sender, EventArgs e)
        {
            try
            {
                string cedulaABorrar = txtCedula.Text; // Obtener la cédula del usuario actual

                // Establecer una conexión con el servidor
                using (TcpClient cliente = new TcpClient())
                {
                    cliente.Connect("localhost", 8888); // Cambia "localhost" y el puerto según corresponda

                    // Enviar solicitud de borrado al servidor
                    string solicitudBorrado = $"BORRADO {cedulaABorrar}";
                    byte[] solicitudBytes = Encoding.UTF8.GetBytes(solicitudBorrado);
                    cliente.GetStream().Write(solicitudBytes, 0, solicitudBytes.Length);

                    // Esperar la respuesta del servidor
                    byte[] buffer = new byte[1024];
                    int bytesRead = cliente.GetStream().Read(buffer, 0, buffer.Length);
                    string respuesta = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                    // Cerrar la conexión con el servidor
                    cliente.Close();

                    // Mostrar un mensaje de confirmación al usuario
                    MessageBox.Show(respuesta, "Borrado de registro", MessageBoxButtons.OK, MessageBoxIcon.Information);

                    // Cerrar la aplicación
                    Application.Exit();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error al borrar el registro: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }


        private void Inicio_Load(object sender, EventArgs e)
        {

            txtCedula.Text = cedulaInicio;

            // Establece una conexión con el servidor
            cliente = new TcpClient();
            cliente.Connect("localhost", 8888);  // Cambia "localhost" y el puerto según corresponda

            // Envía una solicitud de consulta al servidor
            string solicitud = $"CONSULTA {cedulaInicio}";
            byte[] solicitudBytes = Encoding.UTF8.GetBytes(solicitud);
            cliente.GetStream().Write(solicitudBytes, 0, solicitudBytes.Length);

            // Espera la respuesta del servidor
            byte[] buffer = new byte[1024];
            int bytesRead = cliente.GetStream().Read(buffer, 0, buffer.Length);
            string respuesta = Encoding.UTF8.GetString(buffer, 0, bytesRead);

            // Procesa la respuesta y llena los campos correspondientes
            if (!string.IsNullOrEmpty(respuesta) && respuesta.StartsWith("DATOS"))
            {
                string[] datos = respuesta.Split('&');
                if (datos.Length == 9)
                {
                    txtCedula.Text = datos[1];
                    txtNombre.Text = datos[2];
                    txtApellido.Text = datos[3];
                    txtSapellido.Text = datos[4];
                    txtTelefono.Text = datos[5];
                    txtCorreo.Text = datos[6];
                    txtDireccion.Text = datos[7];
                    txtContraseña.Text = datos[8];
                }
            }

            // Cierra la conexión con el servidor
            cliente.Close();

        }
    }
}
