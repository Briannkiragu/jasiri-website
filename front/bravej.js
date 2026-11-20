const bar = document.getElementById('bar');
const nav = document.getElementById('navbar');
const close = document.getElementById('close');

const legacyFooter = document.querySelector('footer:not(.home-footer)');
if (legacyFooter) {
  legacyFooter.outerHTML = `
    <footer class="home-footer">
      <div class="home-footer-brand">
        <a class="brand-mark" href="index.html">JASIRI<span>MCMLXIII</span></a>
        <p>Independent streetwear for the soul rebels.</p>
      </div>
      <div class="home-footer-links">
        <h2>Explore</h2>
        <a href="shop.html">Shop</a>
        <a href="about.html">Our story</a>
        <a href="blog.html">Journal</a>
        <a href="Cart.html">Your cart</a>
      </div>
      <div class="home-footer-contact">
        <h2>Visit us</h2>
        <p>Jevanjee Gardens, Moi Avenue</p>
        <p>Monday to Friday · 10:00–18:00</p>
        <a href="tel:0705061968">0705 061 968</a>
      </div>
      <p class="home-footer-note">© Jasiri. Rooted in Nairobi.</p>
    </footer>`;
}

function setMenuOpen(isOpen) {
  if (!nav) return;
  nav.classList.toggle('active', isOpen);
  close?.classList.toggle('is-visible', isOpen);
  bar?.setAttribute('aria-expanded', String(isOpen));
}

function makeMenuControlAccessible(control, label) {
  if (!control) return;
  control.setAttribute('role', 'button');
  control.setAttribute('tabindex', '0');
  control.setAttribute('aria-label', label);
  control.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      control.click();
    }
  });
}

makeMenuControlAccessible(bar, 'Open navigation menu');
makeMenuControlAccessible(close, 'Close navigation menu');

if (bar && nav) {
  bar.setAttribute('aria-controls', 'navbar');
  bar.setAttribute('aria-expanded', 'false');
  bar.addEventListener('click', () => setMenuOpen(true));
}

if (close && nav) {
  close.addEventListener('click', () => setMenuOpen(false));
}

nav?.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => setMenuOpen(false));
});

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && nav?.classList.contains('active')) {
    setMenuOpen(false);
    bar?.focus();
  }
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 799 && nav?.classList.contains('active')) {
    setMenuOpen(false);
  }
});

/*about zoomblur*/
const feature = document.querySelector('.feature');
if (feature) {
  let animationFrame = 0;
  const updateFeature = () => {
    animationFrame = 0;
    const scrollRange = Math.max(
      document.documentElement.scrollHeight - window.innerHeight,
      1,
    );
    const progress = Math.min(window.scrollY / scrollRange, 1);
    feature.style.backgroundSize = `${250 - progress * 150}%`;
    feature.style.filter = `blur(${progress * 5}px)`;
    feature.style.opacity = String(1 - progress * 0.8);
  };
  window.addEventListener(
    'scroll',
    () => {
      if (!animationFrame) {
        animationFrame = window.requestAnimationFrame(updateFeature);
      }
    },
    { passive: true },
  );
  updateFeature();
}

if (window.jQuery) {
  $(function (){
      var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
      var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);

      if (isChrome || isSafari) {
      } else {
          $('.feature').append('<div class="opaque"></div>');
          $(window).on('scroll', function(){
              var opacity = 0 + ($(window).scrollTop()/5000);
              $('.opaque').css('opacity', opacity);
          });
      }
  });
}

/* Cart module: simple localStorage cart, add-from-products, render on Cart.html */
(function(){
  const STORAGE_KEY = 'jasiri_cart_v1';

  function getCart(){
    const storedCart = localStorage.getItem(STORAGE_KEY);
    if (storedCart === null) return [];

    const cart = JSON.parse(storedCart);
    if (!Array.isArray(cart)) {
      throw new TypeError('Stored cart data must be an array.');
    }
    return cart;
  }
  function updateCartIndicators(cart, animate = false){
    const itemCount = cart.reduce((total, item) => total + (parseInt(item.qty, 10) || 0), 0);
    document.querySelectorAll('a[href="Cart.html"]').forEach(link => {
      if(!link.querySelector('.fa-cart-shopping')) return;
      let indicator = link.querySelector('.cart-count-indicator');
      if(!indicator){
        indicator = document.createElement('span');
        indicator.className = 'cart-count-indicator';
        indicator.setAttribute('aria-hidden', 'true');
        link.appendChild(indicator);
      }
      indicator.textContent = itemCount > 99 ? '99+' : itemCount;
      indicator.hidden = itemCount === 0;
      link.classList.add('cart-indicator-link');
      const label = link.dataset.cartLabel || link.getAttribute('aria-label') || 'View cart';
      link.dataset.cartLabel = label;
      link.setAttribute('aria-label', itemCount ? `${label}, ${itemCount} ${itemCount === 1 ? 'item' : 'items'}` : label);
      if(animate && itemCount){
        indicator.classList.remove('is-updated');
        void indicator.offsetWidth;
        indicator.classList.add('is-updated');
      }
    });
  }
  function saveCart(cart){
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    updateCartIndicators(cart, true);
  }

  function findPriceFromPro(pro){
    const priceEl = pro.querySelector('.price') || pro.querySelector('.description h4') || pro.querySelector('.description h5');
    if(!priceEl) return 0;
    const txt = priceEl.textContent || '';
    const nums = txt.replace(/,/g,'').match(/\d+/g);
    return nums ? parseInt(nums.join('')) : 0;
  }

  function findTitleFromPro(pro){
    const title = pro.querySelector('.catalog-product-name') || pro.querySelector('.description h5') || pro.querySelector('.description span');
    return title?.textContent.trim() || pro.querySelector('img')?.alt?.trim() || 'Product';
  }

  function addToCart(item){
    const cart = getCart();
    // try merge by id (if provided)
    if(item.id){
      const idx = cart.findIndex(i=>i.id===item.id);
      if(idx > -1){ cart[idx].qty += item.qty; saveCart(cart); return; }
    }
    cart.push(item);
    saveCart(cart);
  }

  function getDetailPrice(context){
    const priceEl = context?.querySelector('h2') || context?.querySelector('h4.price') || context?.querySelector('h4');
    if(!priceEl) return 0;
    const txt = priceEl.textContent || '';
    const nums = txt.replace(/,/g,'').match(/\d+/g);
    return nums ? parseInt(nums.join('')) : 0;
  }

  function getDetailTitle(context){
    const titleEl = context?.querySelector('h4') || context?.querySelector('h6') || context?.querySelector('span');
    if(titleEl && titleEl.textContent.trim().length) return titleEl.textContent.trim();
    return context?.querySelector('img')?.alt?.trim() || 'Product';
  }

  function getDetailQty(context){
    const qtyInput = context?.querySelector('input[type=number]');
    if(!qtyInput) return 1;
    const qty = parseInt(qtyInput.value, 10);
    return isNaN(qty) || qty < 1 ? 1 : qty;
  }

  // enhance product cards: inject Add to Cart button if none
  function enhanceProducts(){
    document.querySelectorAll('.pro').forEach(pro=>{
      let btn = pro.querySelector('.add-to-cart');
      if (!btn) {
        btn = document.createElement('button');
        btn.className = 'add-to-cart';
        btn.type = 'button';
        btn.textContent = 'Add to cart';
        const desc = pro.querySelector('.description');
        if (desc) desc.appendChild(btn);
      }
      if (btn.dataset.cartWired) return;
      btn.dataset.cartWired = 'true';
      btn.addEventListener('click', (e)=>{
        e.preventDefault();
        e.stopPropagation();
        const price = findPriceFromPro(pro) || 0;
        const title = findTitleFromPro(pro);
        const img = pro.querySelector('img')?.getAttribute('src') || '';
        const id = (title + '_' + img).replace(/\s+/g,'_').slice(0,120);
        addToCart({ id, title, price, qty:1, img });
        btn.textContent = 'Added to cart';
        btn.classList.add('added');
        setTimeout(() => {
          btn.textContent = 'Add to cart';
          btn.classList.remove('added');
        }, 1400);
      });
    });
  }

  function wireDetailPageCart(){
    document.querySelectorAll('button.normal').forEach(btn => {
      if(!btn.textContent.toLowerCase().includes('add to cart')) return;
      const detailContainer = btn.closest('.single-pro-details');
      if(!detailContainer) return;
      btn.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const price = getDetailPrice(detailContainer) || 0;
        const title = getDetailTitle(detailContainer);
        const qty = getDetailQty(detailContainer);
        const img = document.querySelector('.single-pro-image img')?.getAttribute('src') || '';
        const id = (title + '_' + img).replace(/\s+/g,'_').slice(0,120);
        addToCart({ id, title, price, qty, img });
        btn.textContent = 'Added to cart';
        btn.classList.add('added');
        setTimeout(() => {
          btn.textContent = 'Add to cart';
          btn.classList.remove('added');
        }, 1400);
      });
    });
  }

  // Render cart into Cart.html table
  function renderCartPage(){
    const tbody = document.querySelector('#cart-table tbody');
    if(!tbody) return;
    const cart = getCart();
    tbody.innerHTML = '';
    if(cart.length === 0){
      document.getElementById('cart-empty').style.display = 'block';
    } else {
      document.getElementById('cart-empty').style.display = 'none';
    }
    let total = 0;
    cart.forEach((item, idx)=>{
      const tr = document.createElement('tr');
      tr.className = 'cart-row';
      const subtotal = item.price * item.qty;
      total += subtotal;
      tr.innerHTML = `
        <td style="padding:12px;display:flex;gap:12px;align-items:center">
          <img src="${item.img}" alt="" style="width:80px;height:80px;object-fit:cover">
          <div>
            <div class="cart-title">${item.title}</div>
          </div>
        </td>
        <td style="text-align:center"><span class="cart-price">${item.price}</span></td>
        <td style="text-align:center"><input class="qty" type="number" min="1" value="${item.qty}" style="width:60px;padding:6px;border-radius:4px;border:1px solid #ccc"></td>
        <td style="text-align:center"><span class="cart-sub">${subtotal}</span></td>
        <td style="text-align:center"><button class="remove" data-idx="${idx}" style="background:transparent;border:0;color:#f44336;cursor:pointer">Remove</button></td>
      `;
      tbody.appendChild(tr);
    });
    const totEl = document.getElementById('total');
    const grandEl = document.getElementById('grand');
    if(totEl) totEl.textContent = total;
    if(grandEl) grandEl.textContent = total;
  }

  // wire cart interactions on Cart page
  function wireCartInteractions(){
    document.addEventListener('click', event=>{
      if (!(event.target instanceof Element)) return;
      const removeButton = event.target.closest('.remove');
      if (!removeButton) return;

      const idx = Number.parseInt(removeButton.getAttribute('data-idx'), 10);
      const cart = getCart();
      if (Number.isInteger(idx) && idx >= 0 && idx < cart.length) {
        cart.splice(idx, 1);
        saveCart(cart);
        renderCartPage();
      }
    });
    document.addEventListener('change', event=>{
      if (!(event.target instanceof HTMLInputElement) || !event.target.matches('.qty')) return;

      const row = event.target.closest('.cart-row');
      const tbody = row?.parentElement;
      if (!row || !tbody) return;

      const rows = Array.from(tbody.querySelectorAll('.cart-row'));
      const idx = rows.indexOf(row);
      const cart = getCart();
      const quantity = Number.parseInt(event.target.value, 10);
      const value = Number.isNaN(quantity) || quantity < 1 ? 1 : quantity;
      event.target.value = String(value);

      if (cart[idx]) {
        cart[idx].qty = value;
        saveCart(cart);
        renderCartPage();
      }
    });
  }

  // init
  document.addEventListener('DOMContentLoaded', ()=>{
    updateCartIndicators(getCart());
    enhanceProducts();
    wireDetailPageCart();
    // if on cart page, render
    if(document.querySelector('#cart-table')){
      renderCartPage();
      wireCartInteractions();
    }
  });
  window.addEventListener('storage', e => {
    if(e.key === STORAGE_KEY) updateCartIndicators(getCart(), true);
  });

})();
