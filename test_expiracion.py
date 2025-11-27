from datetime import datetime
import license_validator

print("=" * 60)
print("PRUEBA DEL SISTEMA DE EXPIRACIÓN")
print("=" * 60)

fecha_expiracion = license_validator.FECHA_EXPIRACION
print(f"\nFecha de expiración configurada: {fecha_expiracion.strftime('%d/%m/%Y %H:%M:%S')}")

fecha_web = license_validator.verificar_fecha_web()
if fecha_web:
    print(f"Fecha desde Internet (WorldTimeAPI): {fecha_web.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    print("No se pudo obtener la fecha desde Internet")

fecha_local = license_validator.verificar_fecha_local()
print(f"Fecha local del sistema: {fecha_local.strftime('%d/%m/%Y %H:%M:%S')}")

fecha_verificada = fecha_web if fecha_web else fecha_local

print(f"\nFecha que se usará para validación: {fecha_verificada.strftime('%d/%m/%Y %H:%M:%S')}")

if fecha_verificada > fecha_expiracion:
    print("\n[X] ESTADO: LICENCIA EXPIRADA - El programa NO se ejecutara")
    dias_pasados = (fecha_verificada - fecha_expiracion).days
    print(f"   Han pasado {dias_pasados} dia(s) desde la expiracion")
else:
    dias_restantes = (fecha_expiracion - fecha_verificada).days
    print(f"\n[OK] ESTADO: LICENCIA VALIDA - El programa se ejecutara")
    print(f"   Quedan {dias_restantes} dia(s) antes de la expiracion")

    if dias_restantes <= 7:
        print(f"   [!] ADVERTENCIA: La licencia expirara pronto")

print("\n" + "=" * 60)
