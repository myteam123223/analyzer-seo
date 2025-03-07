# Ejemplo de uso del Analizador de Contenido Competitivo
from competitive_content_analyzer import CompetitiveContentAnalyzer

def main():
    # Crear una instancia del analizador
    analyzer = CompetitiveContentAnalyzer()
    
    # Solicitar URLs al usuario
    print("Analizador de Contenido Competitivo para SEO")
    print("--------------------------------------------")
    print("Ingresa las URLs de tus competidores (una por línea).")
    print("Presiona Enter con una línea vacía para finalizar la lista.")
    
    urls = []
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("Debes ingresar al menos una URL para analizar.")
        return
    
    # Seleccionar idioma
    language = input("Idioma del contenido (es/en) [es]: ").strip().lower() or 'es'
    
    # Seleccionar formato de salida
    output_format = input("Formato de salida (text/excel/json) [excel]: ").strip().lower() or 'excel'
    
    print("\nIniciando análisis, esto puede tardar unos minutos...")
    
    # Realizar el análisis
    results = analyzer.compare_competitors(urls, language=language)
    
    # Generar informe
    report_file = analyzer.generate_report(results, output_format=output_format)
    print(f"\nInforme generado: {report_file}")
    
    # Generar visualizaciones
    print("\nCreando visualizaciones...")
    charts = analyzer.visualize_results(results)
    print(f"Gráficos generados en:")
    print(f"- Palabras clave: {charts['keywords_chart']}")
    print(f"- Estructura: {charts['structure_chart']}")
    
    print("\n¡Análisis completado!")

if __name__ == "__main__":
    main()
