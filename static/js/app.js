// Certificate Request System - Frontend Logic
// Sri Eshwar College of Engineering

document.addEventListener("DOMContentLoaded", function () {
    // 1. Login Page Demo Account Autofill
    const demoPills = document.querySelectorAll(".demo-pill");
    demoPills.forEach(pill => {
        pill.addEventListener("click", function () {
            const u = this.getAttribute("data-username");
            const p = this.getAttribute("data-password");
            const userInput = document.getElementById("username");
            const passInput = document.getElementById("password");
            if (userInput && passInput) {
                userInput.value = u;
                passInput.value = p;
                userInput.focus();
            }
        });
    });

    // 2. Real-time Service Selection & Charge Calculation on Create Request
    const serviceSelect = document.getElementById("service_id");
    const amountInput = document.getElementById("chargeable_amount");
    const chargeDisplay = document.getElementById("calculated_charge_display");
    const serviceStatusDisplay = document.getElementById("service_status_display");
    const serviceAvailDisplay = document.getElementById("service_avail_display");

    function updateCalculatedCharge() {
        if (!amountInput || !chargeDisplay) return;
        const val = parseFloat(amountInput.value);
        if (isNaN(val) || val < 0) {
            chargeDisplay.textContent = "Rs. 0.00";
            return;
        }

        // BR4: If amount < 1000: Rs. 50, If >= 1000: Rs. 0
        if (val < 1000) {
            chargeDisplay.textContent = "Rs. 50.00";
            chargeDisplay.style.color = "#d97706"; // Warning / Charge applied
        } else {
            chargeDisplay.textContent = "Rs. 0.00 (Waived)";
            chargeDisplay.style.color = "#10b981"; // Free / Green
        }
    }

    function updateServiceDetails() {
        if (!serviceSelect) return;
        const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
        if (!selectedOption || !selectedOption.value) {
            if (serviceStatusDisplay) serviceStatusDisplay.textContent = "-";
            if (serviceAvailDisplay) serviceAvailDisplay.textContent = "-";
            return;
        }

        const status = selectedOption.getAttribute("data-status") || "UNKNOWN";
        const avail = selectedOption.getAttribute("data-avail") || "0";

        if (serviceStatusDisplay) {
            serviceStatusDisplay.textContent = status;
            serviceStatusDisplay.className = status === "ACTIVE" ? "badge badge-green" : "badge badge-gray";
        }

        if (serviceAvailDisplay) {
            serviceAvailDisplay.textContent = `${avail} available`;
            if (parseInt(avail) <= 0 || status !== "ACTIVE") {
                serviceAvailDisplay.className = "badge badge-red";
            } else {
                serviceAvailDisplay.className = "badge badge-blue";
            }
        }
    }

    if (amountInput) {
        amountInput.addEventListener("input", updateCalculatedCharge);
        updateCalculatedCharge();
    }

    if (serviceSelect) {
        serviceSelect.addEventListener("change", updateServiceDetails);
        updateServiceDetails();
    }

    // 3. Cancellation Confirmation
    const cancelForms = document.querySelectorAll(".form-cancel-request");
    cancelForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const confirmed = confirm("Are you sure you want to cancel this certificate request? This will release the reserved capacity.");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
