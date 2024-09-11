// Lista de produtos com imagens e informações
const products = [
    { id: 1, name: 'Guitarra Elétrica Stratocaster', price: 'R$ 3.000', image: 'https://www.fender.com/cdn-cgi/image/format=png/https://www.fmicassets.com/Damroot/ZoomJpg/10037/0140510558_fen_ins_frt_1_rr.jpg', link: 'details.html' },
    { id: 2, name: 'Guitarra Acústica', price: 'R$ 1.500', image: 'https://www.fender.com/cdn-cgi/image/format=png/https://www.fmicassets.com/Damroot/ZoomJpg/10037/0140510558_fen_ins_frt_1_rr.jpg', link: 'details.html' },
    // Adicione mais produtos conforme necessário
];

// Função para exibir produtos na página inicial e na página de produtos
function displayProducts() {
    const productContainer = document.querySelector('.product-list');
    if (!productContainer) return; // Verifica se o container existe

    productContainer.innerHTML = ''; // Limpa o container

    products.forEach(product => {
        const productElement = document.createElement('div');
        productElement.classList.add('product');
        
        productElement.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="product-image">
            <h3>${product.name}</h3>
            <p>${product.price}</p>
            <a href="${product.link}">Ver mais</a>
        `;
        
        productContainer.appendChild(productElement);
    });

    // Ajusta o tamanho das imagens após adicionar os produtos
    resizeImages('.product-list .product-image', 200, 150);
}

// Função para ajustar o tamanho das imagens
function resizeImages(selector, width, height) {
    const images = document.querySelectorAll(selector);

    images.forEach(image => {
        image.style.width = `${width}px`;
        image.style.height = `${height}px`;
        image.style.objectFit = 'cover'; // Ajusta a imagem para cobrir o contêiner sem distorcer
    });
}

// Adiciona um listener para carregar os produtos quando o DOM estiver completamente carregado
document.addEventListener('DOMContentLoaded', () => {
    displayProducts();
});

// Funções para o carrossel de imagens
let currentIndex = 0;

function moveSlide(step) {
    const slides = document.querySelectorAll('.carousel-images img');
    const totalSlides = slides.length;
    currentIndex = (currentIndex + step + totalSlides) % totalSlides;
    const offset = -currentIndex * 100;
    document.querySelector('.carousel-images').style.transform = `translateX(${offset}%)`;
}

// Adiciona listeners para as setas do carrossel
document.querySelector('.carousel-prev').addEventListener('click', () => moveSlide(-1));
document.querySelector('.carousel-next').addEventListener('click', () => moveSlide(1));
