import os
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

try:
    import qrcode
except ImportError:
    qrcode = None

# UPI configuration
UPI_ID = os.getenv(
    "TRAVELWRIGHT_UPI_ID",
    "anshuashu2005-1@okaxis",
)
PAYEE_NAME = os.getenv("TRAVELWRIGHT_PAYEE_NAME", "Anshu Kumar")


def generate_upi_link(service: str, description: str, amount: Decimal) -> str:
    """Generate a UPI payment link for the requested amount."""
    params = {
        "pa": UPI_ID,
        "pn": PAYEE_NAME,
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tn": f"Travelwright {service}: {description}"[:80],
    }
    return "upi://pay?" + urlencode(params)


def generate_qr(upi_link: str) -> str:
    """Generate and save the UPI payment QR code if qrcode is installed."""
    if qrcode is None:
        raise RuntimeError("qrcode library is not installed in this environment.")
    qr = qrcode.make(upi_link)
    qr_path = os.path.abspath("travelwright_upi_qr.png")
    qr.save(qr_path)
    return qr_path


def prepare_payment(
    service=None,
    description=None,
    amount=None,
    approval=None,
    interactive: bool = False,
) -> str:
    """
    Prepare a UPI payment link summary.
    Does NOT execute real transactions or verify bank-side payments.
    """
    # Interactive mode ONLY when explicitly run from terminal CLI
    if interactive and service is None:
        print("\n" + "=" * 50)
        print("       TRAVELWRIGHT - UPI PAYMENT")
        print("=" * 50)
        service = input("\nService (hotel/transport/food/other): ").strip()
        description = input("Booking or service details: ").strip()
        amount = input("Amount (INR): ").strip()

    if not service or not str(service).strip():
        return "Error: Service name is required to generate a payment link."

    if not description or not str(description).strip():
        return "Error: Payment details/description are required."

    try:
        parsed_amount = Decimal(str(amount).strip())
        if not parsed_amount.is_finite() or parsed_amount <= 0:
            return "Error: Amount must be greater than zero."
        parsed_amount = parsed_amount.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError):
        return "Error: Enter a valid numeric amount in INR."

    upi_link = generate_upi_link(
        str(service).strip(),
        str(description).strip(),
        parsed_amount,
    )

    qr_note = ""
    if interactive:
        try:
            qr_path = generate_qr(upi_link)
            qr_note = f"\nQR code saved locally at: {qr_path}"
        except Exception as error:
            qr_note = f"\n(QR image not generated: {error})"

    if interactive and approval is None:
        approval = input("\nHave you completed the payment? (yes/no): ").strip().lower()

    status_line = "Status: PENDING (Awaiting user action in UPI app)"
    if str(approval).strip().lower() == "yes":
        status_line = (
            "Status: REPORTED BY USER — PENDING VERIFICATION\n"
            "(Not marked PAID because live bank-side verification is not integrated.)"
        )

    summary = (
        "--- TRAVELWRIGHT UPI PAYMENT LINK (UNVERIFIED / MANUAL) ---\n"
        f"Payee: {PAYEE_NAME}\n"
        f"UPI ID: {UPI_ID}\n"
        f"Service: {service}\n"
        f"Details: {description}\n"
        f"Amount: INR {parsed_amount:.2f}\n"
        f"{status_line}\n"
        f"{qr_note}\n\n"
        f"UPI Deep Link:\n{upi_link}\n\n"
        "IMPORTANT NOTICE:\n"
        "- Travelwright is not connected to a live payment gateway or bank API.\n"
        "- Do not pay unless you have independently verified the booking.\n"
        "- This system cannot verify or confirm incoming bank transactions."
    )
    return summary.strip()


if __name__ == "__main__":
    result = prepare_payment(interactive=True)
    print("\n" + str(result))
    