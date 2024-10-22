let cart = JSON.parse(localStorage.getItem('cart')) || [];
const cartItemsList = document.getElementById('cart-items');
const cartMessage = document.getElementById('cart-message');
const clearCartButton = document.getElementById('clear-cart');
const modal = document.getElementById('productModal');
let currentProduct = {};

function displayCart() {
    cartItemsList.innerHTML = '';
    if (cart.length === 0) {
        cartMessage.classList.add('empty');
        cartMessage.textContent = 'O carrinho está vazio.';
        clearCartButton.style.display = 'none';
    } else {
        cartMessage.classList.remove('empty');
        cartMessage.textContent = `Você tem ${cart.length} itens no carrinho.`;
        clearCartButton.style.display = 'block';

        cart.forEach((item, index) => {
            const li = document.createElement('li');
            li.classList.add('cart-item');
            li.innerHTML = `
                <strong>${item.name}</strong> - R$${item.price.toFixed(2)}
                <button onclick="removeFromCart(${index})">Remover</button>
            `;
            cartItemsList.appendChild(li);
        });
    }
}

function addToCart(product) {
    cart.push(product);
    localStorage.setItem('cart', JSON.stringify(cart));
    displayCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    displayCart();
}

function clearCart() {
    cart = [];
    localStorage.removeItem('cart');
    displayCart();
}

clearCartButton.addEventListener('click', clearCart);

// Modal functions
function openModal(product) {
    currentProduct = product;
    document.getElementById('modalImage').src = product.image;
    document.getElementById('modalTitle').textContent = product.name;
    document.getElementById('modalPrice').textContent = `Preço: R$${product.price.toFixed(2)}`;
    document.getElementById('modalDescription').textContent = product.description;
    modal.style.display = 'block';
}

function closeModal() {
    modal.style.display = 'none';
}

function addToCartFromModal() {
    addToCart(currentProduct);
    closeModal();
}

function buyNow() {
    // Lógica para compra imediata
    alert('Compra realizada!');
    closeModal();
}

// Exibe o carrinho ao carregar a página
document.addEventListener('DOMContentLoaded', displayCart);
