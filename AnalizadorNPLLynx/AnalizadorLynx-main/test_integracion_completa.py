#!/usr/bin/env python3
"""
Test de Integración Completa - Sistema LCLN Dinámico
Verificar que todo funciona end-to-end
"""

import requests
import json
import time
from datetime import datetime

def test_api_health():
    """Test 1: API Health Check"""
    print("🔍 1. Testing API Health...")
    try:
        response = requests.get("http://localhost:8004/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📊 Products: {data['components']['products']}")
            print(f"   📂 Categories: {data['components']['categories']}")
            print(f"   🔄 Cache Updated: {data['components']['cache_updated']}")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return False

def test_nlp_queries():
    """Test 2: NLP Query Processing"""
    print("\n🧠 2. Testing NLP Query Processing...")
    
    queries = [
        ("snacks", "Category search"),
        ("bebidas sin azucar", "Attribute-based search"),
        ("coca cola", "Specific product search"),
        ("productos baratos", "Price filter search"),
        ("doritos", "Brand search")
    ]
    
    all_passed = True
    
    for query, description in queries:
        print(f"\n   Testing: '{query}' ({description})")
        try:
            response = requests.post(
                "http://localhost:8004/api/nlp/analyze",
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                processing_time = data.get("processing_time_ms", 0)
                
                print(f"   ✅ Found: {len(recommendations)} products")
                print(f"   ⏱️  Time: {processing_time:.2f}ms")
                
                # Show first 2 results
                for i, prod in enumerate(recommendations[:2], 1):
                    image_status = "✅" if prod.get("image") else "❌"
                    print(f"      {i}. {prod['name']} - ${prod['price']} {image_status}")
                
                if len(recommendations) == 0:
                    print(f"   ⚠️  No results for '{query}'")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_image_integration():
    """Test 3: Image Integration"""
    print("\n🖼️  3. Testing Image Integration...")
    
    try:
        response = requests.post(
            "http://localhost:8004/api/nlp/analyze",
            json={"query": "coca cola"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            
            images_found = 0
            for prod in recommendations:
                if prod.get("image"):
                    images_found += 1
            
            print(f"   📊 Products with images: {images_found}/{len(recommendations)}")
            
            if images_found > 0:
                sample_prod = next((p for p in recommendations if p.get("image")), None)
                if sample_prod:
                    print(f"   📷 Sample image: {sample_prod['image']}")
                    print("   ✅ Image integration working")
                    return True
            else:
                print("   ❌ No images found")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cache_adaptability():
    """Test 4: Cache Adaptability"""
    print("\n🔄 4. Testing Cache Adaptability...")
    
    try:
        # Check cache refresh endpoint
        response = requests.post("http://localhost:8004/api/force-cache-refresh", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache refresh: {data.get('message', 'Success')}")
            print(f"   📊 Products loaded: {data.get('products_loaded', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Cache refresh failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_performance():
    """Test 5: Performance Test"""
    print("\n⚡ 5. Testing Performance...")
    
    query = "bebidas"
    times = []
    
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:8004/api/nlp/analyze",
                json={"query": query},
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                times.append((end_time - start_time) * 1000)  # Convert to ms
            else:
                print(f"   ❌ Request {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request {i+1} error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"   ⏱️  Average response time: {avg_time:.2f}ms")
        print(f"   📊 All times: {[f'{t:.2f}ms' for t in times]}")
        
        if avg_time < 3000:  # Less than 3 seconds
            print("   ✅ Performance: GOOD")
            return True
        else:
            print("   ⚠️  Performance: NEEDS OPTIMIZATION")
            return False
    else:
        print("   ❌ No successful requests")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 LYNX NLP SYSTEM - INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("API Health", test_api_health),
        ("NLP Processing", test_nlp_queries),
        ("Image Integration", test_image_integration),
        ("Cache Adaptability", test_cache_adaptability),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED - System is fully functional!")
        print("\n🚀 READY FOR PRODUCTION!")
    elif passed >= len(results) * 0.8:  # 80% pass rate
        print("✅ System is mostly functional with minor issues")
    else:
        print("⚠️  System has significant issues that need attention")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
