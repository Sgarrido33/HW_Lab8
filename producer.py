import sys
import argparse
from datetime import datetime
from domain.models import Transaction
from adapters.messaging.rabbit_publisher import RabbitMQPublisher

def main():
    parser = argparse.ArgumentParser(description="Simular registro de transacciones en el Restaurante (Producer).")
    parser.add_argument("--monto", type=float, help="Monto consumido en la cena.")
    parser.add_argument("--tarjeta", type=str, help="Número de tarjeta del cliente.")
    parser.add_argument("--restaurante", type=str, help="Código del restaurante afiliado.")
    
    args = parser.parse_args()

    # Si no se pasan argumentos, pedirlos de forma interactiva
    if args.monto is None or args.tarjeta is None or args.restaurante is None:
        print("--- REGISTRO DE CENA (PRODUCER) ---")
        try:
            monto_str = input("Ingrese el monto consumido: ")
            monto = float(monto_str)
            tarjeta = input("Ingrese el número de tarjeta del cliente: ").strip()
            restaurante = input("Ingrese el código del restaurante afiliado: ").strip()
        except (ValueError, KeyboardInterrupt):
            print("\n [!] Entrada no válida o proceso cancelado.")
            sys.exit(1)
    else:
        monto = args.monto
        tarjeta = args.tarjeta.strip()
        restaurante = args.restaurante.strip()

    fecha_hora = datetime.now().isoformat()

    try:
        # Crear la transacción
        transaction = Transaction(
            monto_consumido=monto,
            tarjeta_cliente=tarjeta,
            codigo_restaurante=restaurante,
            fecha_hora=fecha_hora
        )

        # Publicar la transacción
        publisher = RabbitMQPublisher()
        publisher.publish_transaction(transaction)
        
        print("\n [✓] Transacción registrada y enviada con éxito al broker.")
        print(f"     Monto: ${transaction.monto_consumido:.2f}")
        print(f"     Tarjeta: {transaction.tarjeta_cliente}")
        print(f"     Restaurante: {transaction.codigo_restaurante}")
        print(f"     Fecha/Hora: {transaction.fecha_hora}")

    except ValueError as ve:
        print(f"\n [!] Error de validación: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"\n [!] Ocurrió un error al enviar la transacción: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
