let cart = JSON.parse(localStorage.getItem('cart')) || []; // Carrega o carrinho do localStorage

document.addEventListener('DOMContentLoaded', () => {
    const cartItemsElement = document.getElementById('cart-items');
    const cartMessage = document.getElementById('cart-message');
    const clearCartButton = document.getElementById('clear-cart');

    // Atualiza a visualização do carrinho
    function updateCartDisplay() {
        cartItemsElement.innerHTML = '';
        
        if (cart.length === 0) {
            cartMessage.textContent = 'O carrinho está vazio.';
            clearCartButton.style.display = 'none';
        } else {
            cartMessage.textContent = '';
            cart.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name} - R$ ${item.price.toFixed(2)}`;
                cartItemsElement.appendChild(li);
            });
            clearCartButton.style.display = 'inline';
        }

        localStorage.setItem('cart', JSON.stringify(cart)); // Salva o carrinho no localStorage
    }

    // Adiciona produto ao carrinho
    function addToCart(product) {
        cart.push(product);
        updateCartDisplay();
    }

    // Adiciona produto ao carrinho a partir do modal
    window.addToCartFromModal = function() {
        const title = document.getElementById('modalTitle').innerText;
        const price = parseFloat(document.getElementById('modalPrice').innerText.replace('Preço: ', ''));
        addToCart({ name: title, price: price });
        closeModal();
    };

    // Limpa o carrinho
    clearCartButton.addEventListener('click', () => {
        cart = [];
        updateCartDisplay();
    });

    // Funções para abrir e fechar o modal
    window.openModal = function(title, imageUrl, price, description) {
        document.getElementById('modalTitle').innerText = title;
        document.getElementById('modalImage').src = imageUrl;
        document.getElementById('modalPrice').innerText = 'Preço: ' + price.toFixed(2);
        document.getElementById('modalDescription').innerHTML = description; 
        document.getElementById('productModal').style.display = 'block';
    };

    window.closeModal = function() {
        document.getElementById('productModal').style.display = 'none';
    };

    updateCartDisplay(); // Atualiza a exibição inicial do carrinho
});
