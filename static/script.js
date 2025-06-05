async function cargarProductos() {
  const res = await fetch('/productos');
  const productos = await res.json();
  const select = document.getElementById('producto_id');
  const lista = document.getElementById('lista_productos');
  const alertas = document.getElementById('alertas');
  select.innerHTML = '';
  lista.innerHTML = '';
  alertas.innerHTML = '';

  productos.forEach(p => {
    let option = document.createElement('option');
    option.value = p.id;
    option.textContent = p.nombre;
    select.appendChild(option);

    let li = document.createElement('li');
    li.textContent = `${p.nombre} - ${p.cantidad} unidades - Vence: ${p.fecha_vencimiento}`;
    lista.appendChild(li);

    if (p.cantidad < 5) {
      let div = document.createElement('div');
      div.textContent = `⚠️ Bajo stock: ${p.nombre}`;
      div.style.color = 'red';
      alertas.appendChild(div);
    }
  });
}

async function agregarProducto() {
  const nombre = document.getElementById('nombre').value;
  const fecha = document.getElementById('fecha').value;
  const cantidad = parseInt(document.getElementById('cantidad').value);

  await fetch('/agregar_producto', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre, fecha_vencimiento: fecha, cantidad })
  });

  cargarProductos();
}

async function registrarMovimiento() {
  const producto_id = parseInt(document.getElementById('producto_id').value);
  const tipo = document.getElementById('tipo').value;
  const cantidad = parseInt(document.getElementById('cantidad_mov').value);

  await fetch('/movimiento', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ producto_id, tipo, cantidad })
  });

  cargarProductos();
}

window.onload = cargarProductos;
