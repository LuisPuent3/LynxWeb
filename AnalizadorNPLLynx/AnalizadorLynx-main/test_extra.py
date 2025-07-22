from sistema_lcln_simple import SistemaLCLNSimplificado

def test_extra_queries():
    sistema = SistemaLCLNSimplificado()
    
    consultas_extra = [
        'snacks sin picante',
        'bebidas baratas',
        'productos dulces menores a 15 pesos',
        'coca cola sin azucar'
    ]
    
    for consulta in consultas_extra:
        print(f'\n🔍 CONSULTA: "{consulta}"')
        print('-' * 40)
        resultado = sistema.buscar_productos_inteligente(consulta)
        
        productos = resultado.get('recommendations', [])
        mensaje = resultado.get('user_message', 'Sin mensaje')
        
        print(f'📊 {len(productos)} productos: {mensaje}')
        
        for i, producto in enumerate(productos[:3], 1):
            print(f'  {i}. {producto["nombre"]} - ${producto["precio"]} ({producto["categoria"]})')

if __name__ == "__main__":
    test_extra_queries()
