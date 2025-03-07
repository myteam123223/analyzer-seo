import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import matplotlib.pyplot as plt
import time
from urllib.parse import urlparse
import os
import json

# Asegúrate de descargar los recursos necesarios para NLTK
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class CompetitiveContentAnalyzer:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.spanish_stopwords = set(stopwords.words('spanish'))
        self.english_stopwords = set(stopwords.words('english'))
        
        # Crear directorio para guardar resultados si no existe
        self.results_dir = 'analysis_results'
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
    def get_language_stopwords(self, language='es'):
        """Devuelve el conjunto de stopwords según el idioma especificado"""
        if language.lower() in ['es', 'spanish']:
            return self.spanish_stopwords
        else:
            return self.english_stopwords
    
    def extract_content(self, url):
        """Extrae el contenido de una URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar scripts, estilos y otros elementos no relevantes
            for script in soup(['script', 'style', 'iframe', 'nav', 'footer']):
                script.extract()
            
            # Extraer datos estructurados
            structured_data = {
                'title': soup.title.text.strip() if soup.title else '',
                'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else '',
                'h1_tags': [h1.text.strip() for h1 in soup.find_all('h1')],
                'h2_tags': [h2.text.strip() for h2 in soup.find_all('h2')],
                'h3_tags': [h3.text.strip() for h3 in soup.find_all('h3')],
                'paragraphs': [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 20],
                'links': [a['href'] for a in soup.find_all('a', href=True)],
                'images': [{'src': img.get('src', ''), 'alt': img.get('alt', '')} for img in soup.find_all('img')],
            }
            
            # Extraer el contenido principal (simplificado)
            main_content = ' '.join(structured_data['paragraphs'])
            
            return {
                'url': url,
                'structured_data': structured_data,
                'main_content': main_content,
                'full_html': response.text
            }
        
        except Exception as e:
            print(f"Error al extraer contenido de {url}: {str(e)}")
            return None
    
    def analyze_keywords(self, text, language='es', min_length=3, top_n=30):
        """Analiza las palabras clave más frecuentes en un texto"""
        if not text:
            return []
        
        # Seleccionar stopwords según el idioma
        stop_words = self.get_language_stopwords(language)
        
        # Tokenizar y limpiar el texto
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and len(word) >= min_length and word not in stop_words]
        
        # Contar frecuencias
        word_freq = Counter(words)
        
        # Devolver las palabras más frecuentes
        return word_freq.most_common(top_n)
    
    def analyze_keyword_phrases(self, text, language='es', min_length=2, max_length=4, top_n=20):
        """Analiza frases clave (n-gramas) en el texto"""
        if not text:
            return []
            
        # Seleccionar stopwords según el idioma
        stop_words = self.get_language_stopwords(language)
        
        # Tokenizar y limpiar el texto
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        # Generar n-gramas
        phrases = []
        for n in range(min_length, max_length + 1):
            for i in range(len(words) - n + 1):
                phrases.append(' '.join(words[i:i+n]))
        
        # Contar frecuencias
        phrase_freq = Counter(phrases)
        
        # Devolver las frases más frecuentes
        return phrase_freq.most_common(top_n)
    
    def analyze_content_structure(self, structured_data):
        """Analiza la estructura del contenido"""
        structure_analysis = {
            'title_length': len(structured_data['title']),
            'meta_description_length': len(structured_data['meta_description']),
            'has_h1': len(structured_data['h1_tags']) > 0,
            'h1_count': len(structured_data['h1_tags']),
            'h2_count': len(structured_data['h2_tags']),
            'h3_count': len(structured_data['h3_tags']),
            'paragraph_count': len(structured_data['paragraphs']),
            'avg_paragraph_length': sum(len(p) for p in structured_data['paragraphs']) / len(structured_data['paragraphs']) if structured_data['paragraphs'] else 0,
            'link_count': len(structured_data['links']),
            'image_count': len(structured_data['images']),
            'images_with_alt': sum(1 for img in structured_data['images'] if img['alt']),
        }
        return structure_analysis
    
    def compare_competitors(self, urls, language='es'):
        """Compara el contenido de múltiples competidores"""
        results = []
        all_keywords = Counter()
        all_phrases = Counter()
        
        for url in urls:
            print(f"Analizando: {url}")
            content_data = self.extract_content(url)
            
            if not content_data:
                continue
                
            # Analizar palabras clave
            keywords = self.analyze_keywords(content_data['main_content'], language)
            
            # Analizar frases clave
            phrases = self.analyze_keyword_phrases(content_data['main_content'], language)
            
            # Analizar estructura
            structure = self.analyze_content_structure(content_data['structured_data'])
            
            # Actualizar contadores globales
            for word, count in keywords:
                all_keywords[word] += count
                
            for phrase, count in phrases:
                all_phrases[phrase] += count
            
            # Guardar resultados individuales
            results.append({
                'url': url,
                'domain': urlparse(url).netloc,
                'title': content_data['structured_data']['title'],
                'top_keywords': keywords[:10],
                'top_phrases': phrases[:10],
                'structure': structure
            })
            
            # Pausa entre solicitudes para evitar bloqueos
            time.sleep(2)
        
        # Calcular palabras y frases clave comunes entre competidores
        common_analysis = {
            'common_keywords': all_keywords.most_common(30),
            'common_phrases': all_phrases.most_common(20)
        }
        
        return {
            'individual_results': results,
            'common_analysis': common_analysis
        }
    
    def generate_report(self, comparison_results, output_format='text'):
        """Genera un informe basado en los resultados del análisis"""
        domain_names = [result['domain'] for result in comparison_results['individual_results']]
        
        # Crear un resumen de estructura para comparación
        structure_data = []
        for result in comparison_results['individual_results']:
            data = {'domain': result['domain']}
            data.update(result['structure'])
            structure_data.append(data)
        
        structure_df = pd.DataFrame(structure_data)
        
        # Generar el informe según el formato solicitado
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        if output_format == 'json':
            # Guardar resultados como JSON
            output_file = f"{self.results_dir}/seo_analysis_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(comparison_results, f, ensure_ascii=False, indent=4)
            return output_file
            
        elif output_format in ['excel', 'xlsx']:
            # Guardar resultados en Excel
            output_file = f"{self.results_dir}/seo_analysis_{timestamp}.xlsx"
            
            # Crear un writer de Excel
            with pd.ExcelWriter(output_file) as writer:
                # Hoja de estructura
                structure_df.to_excel(writer, sheet_name='Estructura', index=False)
                
                # Hoja de palabras clave comunes
                common_keywords_df = pd.DataFrame(comparison_results['common_analysis']['common_keywords'], 
                                                 columns=['Palabra', 'Frecuencia'])
                common_keywords_df.to_excel(writer, sheet_name='Keywords Comunes', index=False)
                
                # Hoja de frases comunes
                common_phrases_df = pd.DataFrame(comparison_results['common_analysis']['common_phrases'], 
                                               columns=['Frase', 'Frecuencia'])
                common_phrases_df.to_excel(writer, sheet_name='Frases Comunes', index=False)
                
                # Hojas individuales para cada dominio
                for result in comparison_results['individual_results']:
                    domain = result['domain']
                    # Keywords de este dominio
                    domain_keywords_df = pd.DataFrame(result['top_keywords'], columns=['Palabra', 'Frecuencia'])
                    domain_keywords_df.to_excel(writer, sheet_name=f'{domain[:10]}_Keywords', index=False)
                    
                    # Frases de este dominio
                    domain_phrases_df = pd.DataFrame(result['top_phrases'], columns=['Frase', 'Frecuencia'])
                    domain_phrases_df.to_excel(writer, sheet_name=f'{domain[:10]}_Frases', index=False)
            
            return output_file
            
        else:  # Formato de texto por defecto
            output_file = f"{self.results_dir}/seo_analysis_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== ANÁLISIS DE CONTENIDO COMPETITIVO ===\n\n")
                
                # Escribir resumen general
                f.write("== DOMINIOS ANALIZADOS ==\n")
                for domain in domain_names:
                    f.write(f"- {domain}\n")
                f.write("\n")
                
                # Escribir palabras clave comunes
                f.write("== PALABRAS CLAVE COMUNES ==\n")
                for word, count in comparison_results['common_analysis']['common_keywords'][:15]:
                    f.write(f"{word}: {count}\n")
                f.write("\n")
                
                # Escribir frases clave comunes
                f.write("== FRASES CLAVE COMUNES ==\n")
                for phrase, count in comparison_results['common_analysis']['common_phrases'][:10]:
                    f.write(f"{phrase}: {count}\n")
                f.write("\n")
                
                # Escribir análisis individual
                f.write("== ANÁLISIS INDIVIDUAL ==\n")
                for result in comparison_results['individual_results']:
                    f.write(f"\n--- {result['domain']} ---\n")
                    f.write(f"Título: {result['title']}\n")
                    
                    f.write("\nPalabras clave principales:\n")
                    for word, count in result['top_keywords']:
                        f.write(f"- {word}: {count}\n")
                    
                    f.write("\nFrases clave principales:\n")
                    for phrase, count in result['top_phrases']:
                        f.write(f"- {phrase}: {count}\n")
                    
                    f.write("\nEstructura:\n")
                    for key, value in result['structure'].items():
                        f.write(f"- {key}: {value}\n")
                    f.write("\n")
            
            return output_file

    def visualize_results(self, comparison_results):
        """Visualiza los resultados del análisis"""
        # Crear figuras para visualización
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # 1. Gráfico de barras para palabras clave comunes
        plt.figure(figsize=(12, 6))
        top_keywords = comparison_results['common_analysis']['common_keywords'][:10]
        words, counts = zip(*top_keywords)
        plt.bar(words, counts)
        plt.title('Palabras clave más comunes')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        keywords_chart = f"{self.results_dir}/keywords_{timestamp}.png"
        plt.savefig(keywords_chart)
        
        # 2. Gráfico comparativo de estructura de contenido
        plt.figure(figsize=(12, 8))
        structure_data = []
        domains = []
        
        for result in comparison_results['individual_results']:
            domains.append(result['domain'])
            structure_data.append([
                result['structure']['paragraph_count'],
                result['structure']['h1_count'] + result['structure']['h2_count'] + result['structure']['h3_count'],
                result['structure']['link_count'],
                result['structure']['image_count']
            ])
        
        structure_df = pd.DataFrame(structure_data, 
                                   index=domains,
                                   columns=['Párrafos', 'Encabezados', 'Enlaces', 'Imágenes'])
        
        structure_df.plot(kind='bar', figsize=(12, 6))
        plt.title('Comparación de estructura de contenido')
        plt.ylabel('Cantidad')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        structure_chart = f"{self.results_dir}/structure_{timestamp}.png"
        plt.savefig(structure_chart)
        
        return {
            'keywords_chart': keywords_chart,
            'structure_chart': structure_chart
        }

# Ejemplo de uso
if __name__ == "__main__":
    analyzer = CompetitiveContentAnalyzer()
    
    # Lista de URLs competidoras a analizar
    competitor_urls = [
        'https://www.ejemplo1.com/pagina-relevante',
        'https://www.ejemplo2.com/pagina-similar',
        'https://www.ejemplo3.com/contenido-relacionado'
    ]
    
    # Realizar el análisis
    results = analyzer.compare_competitors(competitor_urls, language='es')
    
    # Generar informe
    report_file = analyzer.generate_report(results, output_format='excel')
    print(f"Informe generado: {report_file}")
    
    # Visualizar resultados
    charts = analyzer.visualize_results(results)
    print(f"Gráficos generados en: {charts['keywords_chart']} y {charts['structure_chart']}")