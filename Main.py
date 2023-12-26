import requests
import tkinter as tk
from tkinter import messagebox, ttk
from folium.plugins import HeatMap
import folium
from PIL import Image, ImageTk
import pandas as pd
import cv2

def get_total_data():
    # Mostrar barra de progreso
    progress_bar.start(10)  # con esto controlo la velocidad de la barra de carga.

    # Obtener datos totales de la API
    url = 'https://olo9de8ie8.execute-api.us-east-2.amazonaws.com/measurements'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        calculate_stats_and_create_map(df)
    else:
        messagebox.showerror("Error", "Error al obtener datos de la API")

    # Ocultar barra de progreso
    progress_bar.stop()

def get_data_by_city():
    # Obtener datos por código postal
    def get_data():
        cp = entry.get()
        if cp and cp.isdigit():
            # Mostrar barra de progreso
            progress_bar.start(10)

            url = f'https://olo9de8ie8.execute-api.us-east-2.amazonaws.com/measurements/cpCity?cpCity={cp}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:  # Si hay datos
                    df = pd.DataFrame(data)
                    calculate_stats_and_create_map(df)
                    top.destroy()
                else:
                    messagebox.showwarning("Advertencia", "No se encontraron registros para ese código postal")
            else:
                messagebox.showerror("Error", "Error al obtener datos de la API")
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un código postal válido")

        # Ocultar barra de progreso
        progress_bar.stop()

    top = tk.Toplevel(root)
    top.title("Datos por ciudad")
    top.geometry("300x120")
    top.resizable(False, False)
    top.configure(bg="#E8E8E8")

    label = tk.Label(top, text="Ingresa el código postal:", bg="#E8E8E8")
    label.pack(pady=5)

    entry = tk.Entry(top)
    entry.pack(pady=5)

    button = tk.Button(top, text="Obtener datos", command=get_data, bg="#4CAF50", fg="white")
    button.pack(pady=5)

def guardar_datos_a_excel(df):
    try:
        file_path = 'datos_guardados.xlsx'
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Éxito", f"Datos guardados correctamente en: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar los datos: {str(e)}")
def descargar_datos():
    def get_data():
        cp = entry.get()
        if cp and cp.isdigit():
            url = f'https://olo9de8ie8.execute-api.us-east-2.amazonaws.com/measurements/cpCity?cpCity={cp}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:  # Si hay datos
                    df = pd.DataFrame(data)
                    guardar_datos_a_excel(df)
                    top.destroy()
                else:
                    messagebox.showwarning("Advertencia", "No se encontraron registros para ese código postal")
            else:
                messagebox.showerror("Error", "Error al obtener datos de la API")
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un código postal válido")

    top = tk.Toplevel(root)
    top.title("Descargar Datos por Ciudad")
    top.geometry("300x120")
    top.resizable(False, False)
    top.configure(bg="#E8E8E8")

    label = tk.Label(top, text="Ingresa el código postal:", bg="#E8E8E8")
    label.pack(pady=5)

    entry = tk.Entry(top)
    entry.pack(pady=5)

    button = tk.Button(top, text="Descargar", command=get_data, bg="#4CAF50", fg="white")
    button.pack(pady=5)
def calculate_stats_and_create_map(df):
    measurement = combo_measurements.get()
    stats_info = f"Estadísticas de '{measurement}':\n"

    measurement_mean = df[measurement].mean()
    measurement_median = df[measurement].median()
    measurement_std = df[measurement].std()
    measurement_min = df[measurement].min()
    measurement_max = df[measurement].max()
    measurement_range = measurement_max - measurement_min

    stats_info += f"Mean: {measurement_mean}\n"
    stats_info += f"Median: {measurement_median}\n"
    stats_info += f"Std Deviation: {measurement_std}\n"
    stats_info += f"Min Value: {measurement_min}\n"
    stats_info += f"Max Value: {measurement_max}\n"
    stats_info += f"Value Range: {measurement_range}\n"

    create_map(df, stats_info)

def create_map(df, stats_info):
    mapa = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
    lat_lng = df[['Latitude', 'Longitude']].values
    heat_map = HeatMap(lat_lng, gradient={0.4: 'blue', 0.65: 'yellow', 1: 'red'}, radius=15, blur=20)
    mapa.add_child(heat_map)

    folium.Marker(
        location=[df['Latitude'].mean(), df['Longitude'].mean()],
        popup=stats_info,
        tooltip="Estadísticas",
        icon=folium.Icon(icon='info-sign')
    ).add_to(mapa)

    file_path = 'mapa_estadisticas.html'
    mapa.save(file_path)
    messagebox.showinfo("Éxito", f"Gráfico generado correctamente. Archivo guardado en: {file_path}")

    # Ocultar barra de progreso
    progress_bar.stop()

root = tk.Tk()
root.title("Visualización de Datos")
root.geometry("300x500")
root.configure(bg="#E8E8E8")



# Cargar la imagen y redimensionarla con OpenCV
image_path = "resources/imagen.jpg"  # Ruta de la imagen
img = cv2.imread(image_path)
img = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)  # Redimensionar la imagen con cv2.resize()

# Convertir la imagen de OpenCV a un objeto PhotoImage de tkinter
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertir BGR a RGB
img = Image.fromarray(img)  # Convertir a formato Image de PIL
img = ImageTk.PhotoImage(image=img)  # Convertir a PhotoImage de tkinter

# Mostrar la imagen en un widget Label
label_img = tk.Label(root, image=img, bg="#E8E8E8")
label_img.pack(pady=10)

label = tk.Label(root, text="Antes de realizar las busquedas,\nselecciona la variable que deseas analizar", bg="#E8E8E8")
label.pack(pady=10)

# Combo box para seleccionar la columna
measurements = ["Temperature1", "Temperature2", "Pressure", "Speed", "Humidity"]
combo_measurements = ttk.Combobox(root, values=measurements)
combo_measurements.pack(pady=5)
combo_measurements.set("Seleccione la columna que desea analizar")

label = tk.Label(root, text="Seleccione una opción:", bg="#E8E8E8")
label.pack(pady=10)


button_descargar = tk.Button(root, text="Descargar datos por ciudad", command=descargar_datos, bg="#4AE046", fg="white")
button_descargar.pack(pady=5)

button_total = tk.Button(root, text="Analizar datos totales", command=get_total_data, bg="#4672E0", fg="white")
button_total.pack(pady=5)

button_city = tk.Button(root, text="Analizar datos por ciudad", command=get_data_by_city, bg="#46E0D9", fg="white")
button_city.pack(pady=5)



# Barra de progreso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
progress_bar.pack(pady=5)

root.mainloop()