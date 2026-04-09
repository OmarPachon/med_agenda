# test_database.py
import database

print("🔍 Probando conexión a MySQL...\n")

if database.test_mysql():
    print("✅ MySQL está disponible")
    
    # Probar obtener pacientes
    pacientes = database.obtener_pacientes_activos()
    if pacientes:
        print(f"\n✅ Primeros 5 pacientes:")
        for p in pacientes[:5]:
            nombre = p.get('nombre_completo', '')
            if not nombre:
                nombre = f"{p.get('primer_nombre', '')} {p.get('primer_apellido', '')}".strip()
            doc = p.get('numero_documento', 'S/N')
            print(f"   - {nombre} ({doc})")
    
    # Probar obtener agenda (AHORA CON limit)
    agenda = database.obtener_agenda_activa(limit=5)
    if agenda:
        print(f"\n✅ Primeras 5 citas:")
        for a in agenda[:5]:
            print(f"   - {a['fecha']} {a['hora']}: {a['numero_documento']}")
    
    # Probar dx
    dx = database.obtener_dx()
    if dx:
        print(f"\n✅ Diagnósticos cargados: {len(dx)}")
    
    # Probar servicios
    servicios = database.obtener_servicios()
    if servicios:
        print(f"✅ Servicios cargados: {len(servicios)}")
    
    # Probar profesionales
    profesionales = database.obtener_profesionales()
    if profesionales:
        print(f"✅ Profesionales cargados: {len(profesionales)}")
else:
    print("❌ MySQL NO está disponible")

print("\n🎉 Prueba completada")