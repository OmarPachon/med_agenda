#!/usr/bin/env python3
"""
Script de Diagnóstico: Identifica pacientes con mismo Num_Doc pero diferente Tipo_Doc
© 2025 Omar Alberto Pachon Pereira
"""
import csv
import os
from collections import defaultdict

def verificar_duplicados_tipo_doc(archivo_csv="data/agenda.csv"):
    """
    Busca pacientes con el mismo número de documento pero diferente tipo de documento.
    """
    if not os.path.exists(archivo_csv):
        print(f"❌ El archivo {archivo_csv} no existe.")
        return
    
    # Diccionario: Num_Doc -> set de Tipo_Doc encontrados
    documentos_por_numero = defaultdict(set)
    # Diccionario: Num_Doc -> lista de nombres asociados (para verificar si es la misma persona)
    nombres_por_numero = defaultdict(set)
    # Diccionario: (Tipo_Doc, Num_Doc) -> lista de registros completos
    registros_por_documento = defaultdict(list)
    
    print("🔍 Leyendo agenda.csv...")
    with open(archivo_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tipo_doc = row.get("Tipo_Doc", "").strip().upper()
            num_doc = row.get("Num_Doc", "").strip()
            nombre = row.get("Nombre_Completo", "").strip()
            
            if not num_doc:
                continue
            
            documentos_por_numero[num_doc].add(tipo_doc)
            nombres_por_numero[num_doc].add(nombre)
            registros_por_documento[(tipo_doc, num_doc)].append(row)
    
    # Identificar casos problemáticos
    casos_problematicos = []
    for num_doc, tipos_doc in documentos_por_numero.items():
        if len(tipos_doc) > 1:
            casos_problematicos.append({
                "num_doc": num_doc,
                "tipos_doc": list(tipos_doc),
                "nombres": list(nombres_por_numero[num_doc]),
                "total_citas": sum(len(registros_por_documento[(td, num_doc)]) for td in tipos_doc)
            })
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("📊 REPORTE DE INCONSISTENCIAS: MISMO Num_Doc CON DIFERENTE Tipo_Doc")
    print("="*80)
    
    if not casos_problematicos:
        print("✅ ¡Excelente! No se encontraron inconsistencias de Tipo_Doc.")
    else:
        print(f"⚠️  Se encontraron {len(casos_problematicos)} paciente(s) con inconsistencias:\n")
        
        for i, caso in enumerate(casos_problematicos, 1):
            print(f"--- CASO #{i} ---")
            print(f"  📄 Número de Documento: {caso['num_doc']}")
            print(f"  🏷️  Tipos de Documento encontrados: {', '.join(caso['tipos_doc'])}")
            print(f"  👤 Nombre(s) registrado(s): {', '.join(caso['nombres'])}")
            print(f"  📅 Total de citas afectadas: {caso['total_citas']}")
            
            # Mostrar detalle de registros
            print(f"  📋 Detalle de registros:")
            for tipo in caso['tipos_doc']:
                cantidad = len(registros_por_documento[(tipo, caso['num_doc'])])
                print(f"      • {tipo}-{caso['num_doc']}: {cantidad} cita(s)")
            print()
    
    print("="*80)
    
    # Guardar reporte en archivo
    archivo_reporte = "data/reporte_inconsistencias_tipo_doc.csv"
    with open(archivo_reporte, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Num_Doc", "Tipos_Doc_Encontrados", "Nombres_Registrados", "Total_Citas", "Detalle"])
        for caso in casos_problematicos:
            detalle = "; ".join([f"{td}={len(registros_por_documento[(td, caso['num_doc'])])}" 
                                 for td in caso['tipos_doc']])
            writer.writerow([
                caso['num_doc'],
                " | ".join(caso['tipos_doc']),
                " | ".join(caso['nombres']),
                caso['total_citas'],
                detalle
            ])
    
    print(f"💾 Reporte guardado en: {archivo_reporte}")
    print("="*80)
    
    return casos_problematicos

if __name__ == "__main__":
    verificar_duplicados_tipo_doc()