const bornDetail = (username, product, amount, rfq) => {
    let t = `<div class="the-detail">
                 <span>${username}</span>
                 <span>${product}</span>
                 <span>${amount}</span>
                 <span>${rfq}</span>
             </div>`
    return t
}
// Two Layers PCB 1-80   53-200.0
// Four Layers PCB 1-60  63-222.22
// Six Layers PCB 1-40  83-244.44
// Eight Layers PCB  1-30  100-250.0
// Ten Layers PCB  1-20  120-280.00
// Twelve Layers PCB  1-15  160-300
// Fourteen Layers PCB  1-15 180-300
// Sixteen Layers PCB  1-15  200-333.33
// Eighteen Layers PCB  1-15  230-355.55
// Twenty Layers PCB    1-15  260.00-400.00
// pcba  10-50 - 1000-3000
// Stencil 1 130
// 给a标签添加herf属性版本
// const bornDetail = (model, stork, href) => {
//     let t = `<li>
//                  <a href=${href} class="left sale-item-name">${model}</a>
//                  <span class="right sale-item-stock">${stork}</span>
//              </li>`
//     return t
// }

const randomName = () => {
    let digit = 'qwertyuiopasdfghjklzxcvbnm'
    let r = ''
    let length = 3
    for (let i = 0; i < length; i++) {
        let index = Math.floor((Math.random() * 26))
        let c = digit[index]
        r += c
    }
    r += '**'
    r = r[0].toLocaleUpperCase() + r.slice(1)
    return r
}

const randomProduct = () => {
    let product = [
        'Two Layers PCB',
        'Four Layers PCB',
        'Six Layers PCB',
        'Eight Layers PCB',
        'Ten Layers PCB',
        'Twelve Layers PCB',
        'Fourteen Layers PCB',
        'Sixteen Layers PCB',
        'Eighteen Layers PCB',
        'Twenty Layers PCB',
        'Pcba',
        'Stencil',
    ]
    let len = product.length
    let index = Math.floor((Math.random() * len))
    return product[index]
}

const randomAmountAndRfq = (type) => {
    let product = {
        'Two Layers PCB' : [80, 53, 100],
        'Four Layers PCB' : [60, 63, 122.22],
        'Six Layers PCB' : [40, 83, 144.44],
        'Eight Layers PCB' : [30, 100, 150],
        'Ten Layers PCB' : [20, 120, 180],
        'Twelve Layers PCB' : [15, 160, 200],
        'Fourteen Layers PCB' : [15, 180, 200],
        'Sixteen Layers PCB' : [15, 200, 233.33],
        'Eighteen Layers PCB' : [15, 230, 255.55],
        'Twenty Layers PCB' : [15, 260, 300],
        'Pcba' : [50, 100, 500],
    }
    if (type === 'Stencil') {
        let amount = 1
        let price = 130
        return [amount, price.toFixed(2)]
    }
    let amount_range = product[type][0]
    let min = product[type][1]
    let max = product[type][2]
    let amount = Math.floor((Math.random() * amount_range)) + 1
    let price = '$ ' + (amount * (Math.random() * (max-min) + min)).toFixed(2)
    return [amount, price]
}

const bornFakeDetail = (n) => {
    let r = []
    for (let i = 0; i < n; i++) {
        let user_name = randomName()
        let product = randomProduct()
        let [amount, price] = randomAmountAndRfq(product)
        let e = [user_name, product, amount, price]
        r.push(e)
    }
    return r
}

const insertDetail = (n) => {
    let sale_list = $('.sale-list')
    let fake_detail = bornFakeDetail(n)
    let new_fake_detail = fake_detail.concat(fake_detail)
    for (let i = 0; i < new_fake_detail.length; i++) {
        let c = new_fake_detail[i]
        let detail = bornDetail(c[0], c[1], c[2], c[3])
        sale_list.append(detail)
    }
}

const autoSumPx = (sale_list, start_index, speed, end_index, ) => {
    let intervalID = setInterval(() => {
        start_index -= 0.5
        let next_index = start_index + 'px'
        sale_list.css('top', next_index)
        if (start_index === end_index) {
            start_index = -5
        }
    }, speed)
    return intervalID
}
// 解决突兀滚动的方法：设置两个一样的表连在一起，总高height，
// if(start_index === -height/2)，
// let start_index = -(height - scroll.height)
// 现在我是随机生成的数据所以不好搞，用特定数据的话可以这样解决

const autoScroll = () => {
    let sale_list = $('.sale-list')
    let sale_list_top = sale_list.css('top')
    let sale_list_height_str = sale_list.css('height')
    let sale_list_height = Number(sale_list_height_str.slice(0, -2))
    let end_index = -(sale_list_height / 2)
    let start_index = Number(sale_list_top.slice(0, -2))
    let intervalID = autoSumPx(sale_list, start_index, 100, end_index)
    return intervalID
}

const bindEvent = () => {
    let intervalID = autoScroll()
    let container = $('.hot-sale-container')
    container.on('mouseover', () => {
        clearInterval(intervalID)
    })
    container.on('mouseout', () => {
        intervalID = autoScroll()
    })
}

const __main = () => {
    insertDetail(50)
    bindEvent()
}

__main()