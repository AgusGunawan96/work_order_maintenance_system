// File: assets/js/custom/location-machine-filter.js

document.addEventListener('DOMContentLoaded', function() {
    const locationSelect = document.getElementById('location');
    const machineSelect = document.getElementById('machine');

    locationSelect.addEventListener('change', function() {
        const locationId = this.value;

        // Kosongkan opsi mesin sebelumnya
        machineSelect.innerHTML = '<option value="">-- Pilih Mesin --</option>';

        if (locationId) {
            fetch(`/get_machines_by_location/${locationId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log(data);  // Untuk memeriksa data yang diterima dari server
                    data.forEach(machine => {
                        const option = document.createElement('option');
                        option.value = machine.id;
                        option.textContent = machine.name;
                        machineSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Gagal mengambil data mesin:', error));
        }
    });
});
