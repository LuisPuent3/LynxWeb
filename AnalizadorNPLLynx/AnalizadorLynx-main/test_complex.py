from sistema_lcln_simple import SistemaLCLNSimplificado

def test_queries():
    sistema = SistemaLCLNSimplificado()
    
    consultas_test = [
        'botana sin picante mayor a 5 pesos',
        'productos con picante',
        'dulces populares', 
        'frutas frescas de temporada'
    ]
    
    for consulta in consultas_test:
        print(f'\n🔍 CONSULTA: "{consulta}"')
        print('=' * 50)
        resultado = sistema.buscar_productos_inteligente(consulta)
        
        productos = resultado.get('recommendations', [])
        mensaje = resultado.get('user_message', 'Sin mensaje')
        
        print(f'📊 Productos encontrados: {len(productos)}')
        print(f'💬 Mensaje: {mensaje}')
        
        for i, producto in enumerate(productos[:3], 1):
            print(f'  {i}. {producto["nombre"]} - ${producto["precio"]} ({producto["categoria"]})')
        
        if len(productos) > 3:
            print(f'  ... y {len(productos) - 3} más')

if __name__ == "__main__":
    test_queries()
