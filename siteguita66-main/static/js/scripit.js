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
    startCarousel(); // Inicia o carrossel automático
});

// Função para mover o slide
function moveSlide(step) {
    const slides = document.querySelectorAll('.slider-content .slides img');
    const totalSlides = slides.length;
    const sliderContainer = document.querySelector('.slider-content .slides');
    if (!sliderContainer) return;

    currentIndex = (currentIndex + step + totalSlides) % totalSlides;
    const offset = -currentIndex * 100;
    sliderContainer.style.transform = `translateX(${offset}%)`;
}

// Adiciona listeners para as setas do carrossel
document.querySelector('.carousel-prev').addEventListener('click', () => moveSlide(-1));
document.querySelector('.carousel-next').addEventListener('click', () => moveSlide(1));

// Função para iniciar o carrossel automático
function startCarousel() {
    const radios = document.querySelectorAll('#carousel input[type="radio"]');
    if (radios.length === 0) return; // Verifica se há radios para o carrossel

    let currentIndex = 0;
    const totalSlides = radios.length;

    function moveToNextSlide() {
        radios[currentIndex].checked = false;
        currentIndex = (currentIndex + 1) % totalSlides;
        radios[currentIndex].checked = true;
        moveSlide(1); // Mover o slide para a próxima posição
    }

    // Muda para o próximo slide a cada 3 segundos (3000 milissegundos)
    setInterval(moveToNextSlide, 3000);
}

// Função para alterar a cor do cabeçalho ao rolar
document.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
