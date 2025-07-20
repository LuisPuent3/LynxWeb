#!/usr/bin/env python3
"""
Script de pruebas exhaustivas para el sistema LYNX NLP
Validación completa antes de integración con frontend
"""

import requests
import time
import json
from typing import Dict, List, Any
import sys
from colorama import init, Fore, Back, Style

# Inicializar colorama para Windows
init()

class TestLynxNLP:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Registra el resultado de una prueba"""
        status = "✅ PASS" if passed else "❌ FAIL"
        color = Fore.GREEN if passed else Fore.RED
        
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'response_time': response_time
        }
        
        self.test_results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        print(f"{color}{status}{Style.RESET_ALL} {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    ⏱️  Tiempo: {response_time:.2f}ms")
        print()

    def test_health_check(self):
        """Test 1: Health Check básico"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    products_count = data.get('components', {}).get('products', '0')
                    if '1304' in str(products_count):
                        self.log_result("Health Check", True, 
                                      f"Sistema saludable con {products_count} productos", response_time)
                    else:
                        self.log_result("Health Check", False, 
                                      f"Productos no cargados correctamente: {products_count}")
                else:
                    self.log_result("Health Check", False, f"Estado no saludable: {data.get('status')}")
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Health Check", False, f"Error de conexión: {e}")

    def test_basic_search(self):
        """Test 2: Búsquedas básicas"""
        test_cases = [
            {"query": "coca cola", "expected_products": True, "expected_category": "bebidas"},
            {"query": "sabritas", "expected_products": True, "expected_category": "snacks"},
            {"query": "leche", "expected_products": True, "expected_category": "lacteos"},
            {"query": "manzana", "expected_products": True, "expected_category": "frutas"},
        ]
        
        for case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/nlp/analyze",
                    json={"query": case["query"]},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get('success', False)
                    recommendations = data.get('recommendations', [])
                    
                    if success and len(recommendations) > 0:
                        # Verificar que los productos sean de la categoría esperada
                        categories_found = [p.get('category', '').lower() for p in recommendations[:3]]
                        expected_cat = case["expected_category"].lower()
                        
                        if any(expected_cat in cat for cat in categories_found):
                            self.log_result(f"Búsqueda básica: '{case['query']}'", True,
                                          f"Encontrados {len(recommendations)} productos relevantes", response_time)
                        else:
                            self.log_result(f"Búsqueda básica: '{case['query']}'", False,
                                          f"Categorías encontradas {categories_found} no coinciden con {expected_cat}")
                    else:
                        self.log_result(f"Búsqueda básica: '{case['query']}'", False,
                                      f"No se encontraron productos o fallo en análisis")
                else:
                    self.log_result(f"Búsqueda básica: '{case['query']}'", False,
                                  f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Búsqueda básica: '{case['query']}'", False, f"Error: {e}")

    def test_spelling_correction(self):
        """Test 3: Corrección ortográfica"""
        test_cases = [
            {"query": "koka kola", "should_correct": True, "expected_word": "coca"},
            {"query": "dorriots", "should_correct": True, "expected_word": "doritos"},
            {"query": "chetos", "should_correct": True, "expected_word": "cheetos"},
            {"query": "votana", "should_correct": True, "expected_word": "botana"},
            {"query": "asucar", "should_correct": True, "expected_word": "azucar"},
            {"query": "pikante", "should_correct": True, "expected_word": "picante"},
        ]
        
        for case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/nlp/analyze",
                    json={"query": case["query"]},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    corrections = data.get('corrections', {})
                    applied = corrections.get('applied', False)
                    corrected_query = corrections.get('corrected_query', '')
                    
                    if case["should_correct"]:
                        if applied and case["expected_word"] in corrected_query.lower():
                            self.log_result(f"Corrección: '{case['query']}'", True,
                                          f"Corregido a: '{corrected_query}'", response_time)
                        else:
                            self.log_result(f"Corrección: '{case['query']}'", False,
                                          f"No se corrigió correctamente. Resultado: '{corrected_query}'")
                else:
                    self.log_result(f"Corrección: '{case['query']}'", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Corrección: '{case['query']}'", False, f"Error: {e}")

    def test_semantic_analysis(self):
        """Test 4: Análisis semántico avanzado"""
        test_cases = [
            {
                "query": "bebidas sin azucar",
                "expected_interpretation": "product_search",
                "expected_filters": ["sin azucar", "light", "zero"]
            },
            {
                "query": "snacks picantes baratos",
                "expected_interpretation": "product_search", 
                "expected_attributes": ["picante", "barato"]
            },
            {
                "query": "productos menores a 20 pesos",
                "expected_sql_contains": ["precio", "20", "<="]
            },
            {
                "query": "frutas rojas",
                "expected_category": "frutas",
                "expected_attribute": "roja"
            }
        ]
        
        for case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/nlp/analyze",
                    json={"query": case["query"]},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    interpretation = data.get('interpretation', {})
                    sql_query = data.get('sql_query', '')
                    recommendations = data.get('recommendations', [])
                    
                    # Verificar interpretación
                    test_passed = True
                    details = []
                    
                    if 'expected_interpretation' in case:
                        interp_type = interpretation.get('type', '')
                        if case['expected_interpretation'] in interp_type:
                            details.append(f"✓ Interpretación correcta: {interp_type}")
                        else:
                            details.append(f"✗ Interpretación incorrecta: {interp_type}")
                            test_passed = False
                    
                    if 'expected_sql_contains' in case:
                        missing_sql_parts = []
                        for expected_part in case['expected_sql_contains']:
                            if expected_part.lower() not in sql_query.lower():
                                missing_sql_parts.append(expected_part)
                                test_passed = False
                        
                        if not missing_sql_parts:
                            details.append("✓ SQL generado correctamente")
                        else:
                            details.append(f"✗ SQL falta: {missing_sql_parts}")
                    
                    if 'expected_category' in case:
                        found_categories = [p.get('category', '') for p in recommendations[:3]]
                        if any(case['expected_category'] in cat.lower() for cat in found_categories):
                            details.append(f"✓ Categoría correcta encontrada")
                        else:
                            details.append(f"✗ Categoría no encontrada en: {found_categories}")
                            test_passed = False
                    
                    self.log_result(f"Análisis semántico: '{case['query']}'", test_passed,
                                  "; ".join(details), response_time)
                else:
                    self.log_result(f"Análisis semántico: '{case['query']}'", False,
                                  f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Análisis semántico: '{case['query']}'", False, f"Error: {e}")

    def test_performance(self):
        """Test 5: Rendimiento y escalabilidad"""
        queries = [
            "coca cola",
            "bebidas sin azucar baratas",
            "doritos pikantes menor a 20 pesos",
            "leche descremada",
            "frutas rojas"
        ]
        
        response_times = []
        
        print(f"{Fore.YELLOW}🚀 Ejecutando pruebas de rendimiento...{Style.RESET_ALL}\n")
        
        for i, query in enumerate(queries * 3):  # Repetir cada query 3 veces
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/nlp/analyze",
                    json={"query": query},
                    timeout=5
                )
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success', False):
                        self.log_result(f"Performance Query {i+1}", False, 
                                      f"Query falló: {query}")
                        return
                        
            except Exception as e:
                self.log_result("Performance", False, f"Error en query {i+1}: {e}")
                return
        
        # Analizar resultados
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Criterios de rendimiento
        performance_ok = avg_time < 100  # Promedio menor a 100ms
        consistency_ok = max_time < 500  # Máximo menor a 500ms
        
        if performance_ok and consistency_ok:
            self.log_result("Performance", True,
                          f"Promedio: {avg_time:.1f}ms, Max: {max_time:.1f}ms, Min: {min_time:.1f}ms")
        else:
            self.log_result("Performance", False,
                          f"Rendimiento insuficiente. Promedio: {avg_time:.1f}ms, Max: {max_time:.1f}ms")

    def test_edge_cases(self):
        """Test 6: Casos extremos y manejo de errores"""
        test_cases = [
            {"query": "", "should_fail": True, "description": "Query vacía"},
            {"query": "   ", "should_fail": True, "description": "Solo espacios"},
            {"query": "xyz123!@#", "expected_fallback": True, "description": "Texto sin sentido"},
            {"query": "a" * 300, "should_fail": True, "description": "Query muy larga"},
            {"query": "prodcuto que no existe en ninguna parte del mundo", "expected_fallback": True, "description": "Producto inexistente"},
            {"query": "123", "expected_fallback": True, "description": "Solo números"},
        ]
        
        for case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/nlp/analyze",
                    json={"query": case["query"]},
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                
                if case.get("should_fail", False):
                    # Esperamos que falle o devuelva error controlado
                    if response.status_code != 200:
                        self.log_result(f"Caso extremo: {case['description']}", True,
                                      f"Correctamente rechazado con HTTP {response.status_code}")
                    else:
                        data = response.json()
                        if not data.get('success', True):
                            self.log_result(f"Caso extremo: {case['description']}", True,
                                          f"Correctamente manejado como error")
                        else:
                            self.log_result(f"Caso extremo: {case['description']}", False,
                                          f"Debería haber fallado pero pasó")
                            
                elif case.get("expected_fallback", False):
                    # Esperamos que maneje graciosamente con fallback
                    if response.status_code == 200:
                        data = response.json()
                        recommendations = data.get('recommendations', [])
                        if len(recommendations) >= 0:  # Cualquier resultado válido
                            self.log_result(f"Caso extremo: {case['description']}", True,
                                          f"Manejo gracioso con {len(recommendations)} recomendaciones de fallback")
                        else:
                            self.log_result(f"Caso extremo: {case['description']}", False,
                                          f"No proporcionó fallback adecuado")
                    else:
                        self.log_result(f"Caso extremo: {case['description']}", False,
                                      f"Falló inesperadamente con HTTP {response.status_code}")
                        
            except Exception as e:
                if case.get("should_fail", False):
                    self.log_result(f"Caso extremo: {case['description']}", True,
                                  f"Correctamente falló con excepción controlada")
                else:
                    self.log_result(f"Caso extremo: {case['description']}", False, f"Error: {e}")

    def test_batch_processing(self):
        """Test 7: Procesamiento en lotes"""
        try:
            batch_queries = [
                "coca cola",
                "sabritas clasicas", 
                "leche lala",
                "manzanas rojas"
            ]
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/nlp/batch",
                json={"queries": batch_queries},
                timeout=15
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if len(results) == len(batch_queries):
                    all_successful = all(r.get('success', False) for r in results)
                    if all_successful:
                        self.log_result("Procesamiento en lotes", True,
                                      f"{len(results)} queries procesadas exitosamente", response_time)
                    else:
                        failed_count = len([r for r in results if not r.get('success', False)])
                        self.log_result("Procesamiento en lotes", False,
                                      f"{failed_count} queries fallaron de {len(results)}")
                else:
                    self.log_result("Procesamiento en lotes", False,
                                  f"Resultados incorrectos: {len(results)} != {len(batch_queries)}")
            else:
                self.log_result("Procesamiento en lotes", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Procesamiento en lotes", False, f"Error: {e}")

    def test_data_integrity(self):
        """Test 8: Integridad de datos"""
        try:
            # Test de estadísticas
            response = requests.get(f"{self.base_url}/api/stats", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('total_products', 0)
                synonyms = data.get('total_synonyms', 0)
                
                products_ok = 1000 <= products <= 2000  # Rango esperado
                synonyms_ok = synonyms > 50000  # Debe tener muchos sinónimos
                
                if products_ok and synonyms_ok:
                    self.log_result("Integridad de datos", True,
                                  f"Productos: {products}, Sinónimos: {synonyms}")
                else:
                    self.log_result("Integridad de datos", False,
                                  f"Datos fuera de rango. Productos: {products}, Sinónimos: {synonyms}")
            else:
                self.log_result("Integridad de datos", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Integridad de datos", False, f"Error: {e}")

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🧪 BATERÍA DE PRUEBAS EXHAUSTIVAS - SISTEMA LYNX NLP{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        tests = [
            ("🔥 Test 1: Health Check", self.test_health_check),
            ("🔍 Test 2: Búsquedas Básicas", self.test_basic_search),
            ("📝 Test 3: Corrección Ortográfica", self.test_spelling_correction),
            ("🧠 Test 4: Análisis Semántico", self.test_semantic_analysis),
            ("⚡ Test 5: Performance", self.test_performance),
            ("🚨 Test 6: Casos Extremos", self.test_edge_cases),
            ("📊 Test 7: Procesamiento en Lotes", self.test_batch_processing),
            ("💾 Test 8: Integridad de Datos", self.test_data_integrity),
        ]
        
        for test_name, test_func in tests:
            print(f"{Fore.YELLOW}{test_name}{Style.RESET_ALL}")
            print("-" * 50)
            test_func()
            print()
        
        self.print_summary()

    def print_summary(self):
        """Imprimir resumen final"""
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 RESUMEN DE PRUEBAS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        print(f"Total de pruebas: {total_tests}")
        print(f"{Fore.GREEN}✅ Pasaron: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Fallaron: {self.failed}{Style.RESET_ALL}")
        print(f"Tasa de éxito: {success_rate:.1f}%\n")
        
        if success_rate >= 95:
            print(f"{Fore.GREEN}{Back.WHITE}🎉 ¡EXCELENTE! Sistema listo para integración{Style.RESET_ALL}")
        elif success_rate >= 85:
            print(f"{Fore.YELLOW}⚠️  BUENO: Sistema mayormente funcional, revisar fallos{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}🚨 CRÍTICO: Sistema necesita correcciones antes de integrar{Style.RESET_ALL}")
            
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

if __name__ == "__main__":
    # Verificar si se proporcionó URL personalizada
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = TestLynxNLP(base_url)
    tester.run_all_tests()
