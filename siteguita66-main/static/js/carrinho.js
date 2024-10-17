// Adiciona itens ao carrinho
document.querySelectorAll('.menu-item a').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const itemName = this.getAttribute('data-name');
        const itemPrice = parseFloat(this.getAttribute('data-price'));

        const orderItemsList = document.getElementById('order-items');
        const li = document.createElement('li');
        li.textContent = `${itemName} - R$ ${itemPrice.toFixed(2)}`;
        
        // Criação do ícone de remoção
        const removeIcon = document.createElement('i');
        removeIcon.className = 'fas fa-trash-alt';
        removeIcon.style.cursor = 'pointer';
        removeIcon.addEventListener('click', function() {
            orderItemsList.removeChild(li);
            total -= itemPrice;
            cartCount--;
            document.getElementById('cart-count').textContent = cartCount;
            document.getElementById('order-total').textContent = `Total: R$ ${total.toFixed(2)}`;
        });

        li.appendChild(removeIcon);
        orderItemsList.appendChild(li);

        total += itemPrice;
        cartCount++;
        document.getElementById('cart-count').textContent = cartCount;
        document.getElementById('order-total').textContent = `Total: R$ ${total.toFixed(2)}`;
    });
});
document.getElementById('delivery-form').addEventListener('submit', function(event) {
event.preventDefault();

// Captura a opção de entrega selecionada
const deliveryOption = document.querySelector('input[name="delivery-option"]:checked');
const selectedDelivery = deliveryOption ? deliveryOption.value : 'Nenhuma opção selecionada';

// Captura o método de pagamento selecionado
const paymentMethod = document.querySelector('input[name="payment-method"]:checked');
const selectedPayment = paymentMethod ? paymentMethod.value : 'Nenhum método de pagamento selecionado';

// Mensagem de sucesso
const successMessage = document.createElement('div');
successMessage.className = 'alert alert-success';
successMessage.textContent = "Compra finalizada com sucesso! Obrigado, " + document.getElementById('name').value + 
                         ". Opção de entrega: " + selectedDelivery + 
                         ". Método de pagamento: " + selectedPayment;

document.querySelector('.modal-body').prepend(successMessage);
// Aqui você poderia adicionar a lógica para enviar os dados do pedido ao servidor
});

