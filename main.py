from tkinter import *
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from PIL import Image, ImageTk


def isNameExist(phone):
    # 检查 CSV 文件中是否已有该电话的会员
    with open('members.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == phone:
                return True
    return False

def addMember(name, phone, balance):
    # 检查电话是否已存在
    if isNameExist(phone):
        return False  # 电话重复，不能添加

    # 将输入的会员信息写入 CSV 文件
    with open('members.csv', 'a', newline='', encoding='utf-8') as file:  # 以追加模式打开文件 'a'
        writer = csv.writer(file)
        writer.writerow([name, phone, balance])

    # 获取当前的日期和时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建日志文件，并记录日志
    log_filename = f"{phone}.log"
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{current_time} {phone} 充值 {balance} 元\n")
    
    return True

def updateMember(phone, new_name, new_phone, new_balance):
    # 读取现有的会员信息并更新
    members = []
    updated = False

    with open('members.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        members = list(reader)

    # 修改目标会员的记录
    for i, member in enumerate(members):
        if member[1] == phone:
            if new_balance is not None:  # 余额变动时
                current_balance = float(member[2])
                new_balance = float(new_balance)
                member[2] = str(current_balance + new_balance) if new_balance > 0 else str(current_balance + new_balance)
            else:
                member[2] = current_balance
            if new_phone is not None:  # 电话变动时
                member[1] = new_phone
            else:
                member[1] = phone
            if new_name is not None:  # 姓名变动时
                member[0] = new_name
            else:
                member[0] = member[0]
            updated = True
            break

    if updated:
        with open('members.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(members)
        
        # 获取当前的日期和时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 记录修改日志
        log_filename = f"{new_phone}.log" if new_phone else f"{phone}.log"
        with open(log_filename, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{current_time} {new_name if new_name else member[0]} 修改电话为 {new_phone if new_phone else member[1]}，余额为 {member[2]} 元\n")
        
        return True
    else:
        return False

def openAddMemberWindow():
    # 创建一个新窗口
    add_window = Toplevel(root)
    add_window.title("添加会员")
    
    # 窗口内容
    ttk.Label(add_window, text="姓名:").grid(column=0, row=0)
    name_entry = ttk.Entry(add_window)
    name_entry.grid(column=1, row=0)
    
    ttk.Label(add_window, text="电话:").grid(column=0, row=1)
    phone_entry = ttk.Entry(add_window)
    phone_entry.grid(column=1, row=1)
    
    ttk.Label(add_window, text="余额:").grid(column=0, row=2)
    balance_entry = ttk.Entry(add_window)
    balance_entry.grid(column=1, row=2)
    
    # 提交按钮
    def submit():
        name = name_entry.get()
        phone = phone_entry.get()
        balance = float(balance_entry.get())
        
        # 尝试添加会员，如果姓名重复则给出提示
        if addMember(name, phone, balance):
            add_window.destroy()  # 关闭新窗口
        else:
            # 显示提示信息
            error_label.config(text="该会员(电话)已存在")
            error_label.grid(column=0, row=4, columnspan=2)  # 确保提示信息在新的行中

    # 提交按钮
    ttk.Button(add_window, text="提交", command=submit).grid(column=1, row=3)
    
    # 提示信息标签，初始为空
    error_label = ttk.Label(add_window, text="")
    error_label.grid(column=0, row=4, columnspan=2)  # 默认在第四行显示（空行）

def openUpdateMemberWindow():
    # 创建一个新窗口
    edit_window = Toplevel(root)
    edit_window.title("编辑会员")

    ttk.Label(edit_window, text="(原)电话:").grid(column=0, row=0)
    phone_entry = ttk.Entry(edit_window)
    phone_entry.grid(column=1, row=0)
    
    ttk.Label(edit_window, text="新的姓名:").grid(column=0, row=1)
    new_name_entry = ttk.Entry(edit_window)
    new_name_entry.grid(column=1, row=1)

    ttk.Label(edit_window, text="新的电话:").grid(column=0, row=2)
    new_phone_entry = ttk.Entry(edit_window)
    new_phone_entry.grid(column=1, row=2)

    ttk.Label(edit_window, text="新的余额 (+金额 或 -金额):").grid(column=0, row=3)
    balance_entry = ttk.Entry(edit_window)
    balance_entry.grid(column=1, row=3)

    # 提交按钮
    def submit():
        phone = phone_entry.get()
        new_name = new_name_entry.get()
        new_phone = new_phone_entry.get()
        balance = balance_entry.get()
        
        # 检查输入框是否为空
        if phone == "" or new_name == "" or new_phone == "" or balance == "":
            errlabel = ttk.Label(edit_window, text="有输入框为空！").grid(column=0, row=4, columnspan=2)
        else:
            if updateMember(phone, new_name, new_phone, balance):
                edit_window.destroy()  # 关闭编辑窗口
            else:
                errlabel = ttk.Label(edit_window, text="未找到该会员！").grid(column=0, row=4, columnspan=2)

    ttk.Button(edit_window, text="提交", command=submit).grid(column=1, row=5)

def deleteMember(delete_info):
    found = False  # 标记是否找到该会员
    updated_members = []  # 用于保存更新后的会员数据

    # 打开并读取 members.csv 文件
    try:
        with open('members.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)  # 以字典形式读取数据
            for row in reader:
                if row['name'] == delete_info or row['phone'] == delete_info:
                    found = True  # 找到要删除的会员
                else:
                    updated_members.append(row)  # 保留不需要删除的会员
    except FileNotFoundError:
        print("文件未找到，请确保 members.csv 存在。")
        return False

    # 如果找到了会员，重新写入更新后的文件
    if found:
        try:
            with open('members.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'phone', 'balance']  # 假设 CSV 文件包含这些字段
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # 写入表头
                writer.writerows(updated_members)  # 写入更新后的会员数据
            return True
        except Exception as e:
            print(f"写入文件时出错: {e}")
            return False
    else:
        return False  # 没有找到会员

def openDeleteMemberWindow():
    # 创建删除会员窗口
    delete_window = Toplevel(root)
    delete_window.title("删除会员")
    
    # 窗口内容
    ttk.Label(delete_window, text="输入会员电话:").grid(column=0, row=0)
    delete_entry = ttk.Entry(delete_window)
    delete_entry.grid(column=1, row=0)
    
    # 提交按钮逻辑
    def submit_delete():
        delete_info = delete_entry.get()  # 获取输入的姓名或电话
        
        # 删除会员
        if deleteMember(delete_info):
            delete_window.destroy()  # 关闭窗口
        else:
            success_label.config(text="未找到该会员，请检查电话！")
        
        # 显示提示信息
        success_label.grid(column=0, row=2, columnspan=2)
    
    # 提交按钮
    ttk.Button(delete_window, text="删除", command=submit_delete).grid(column=1, row=1)
    
    # 提示信息标签，初始为空
    success_label = ttk.Label(delete_window, text="")
    success_label.grid(column=0, row=2, columnspan=2)  # 默认在第二行显示（空行）

root = Tk()
top = Menu(root)
menuMainprog = Menu(top)
menuMembersExec = Menu(menuMainprog)
top.add_cascade(label="主程序", menu=menuMainprog)
menuMainprog.add_cascade(label="会员操作", menu=menuMembersExec)

# 点击添加会员时打开新窗口
menuMembersExec.add_command(label="添加会员", command=openAddMemberWindow, accelerator='Ctrl+N')
# 点击编辑会员时打开新窗口
menuMembersExec.add_command(label="编辑会员", command=openUpdateMemberWindow, accelerator='Ctrl+U')
# 点击删除会员时打开新窗口
menuMembersExec.add_command(label="删除会员", command=openDeleteMemberWindow, accelerator='Ctrl+D')
menuMainprog.add_command(label="退出", command=root.destroy, accelerator='Ctrl+Alt')

root.config(menu=top)  # 将菜单栏配置到主窗口
root.title('Quickest收银系统')

# 读取商品数据
def load_goods_data():
    goods_data = {}
    try:
        with open('goodsdata.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # 假设每行的格式是 [商品名称, 商品价格, 商品编号]
                if len(row) == 3:
                    goods_data[row[2]] = {"name": row[0], "price": row[1]}  # 使用商品编号作为键
    except FileNotFoundError:
        print("goodsdata.csv 文件未找到!")
    return goods_data

# 读取会员数据
def load_members_data():
    members_data = {}
    try:
        with open('members.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # 跳过第一行
            for row in reader:
                # 假设每行的格式是 [姓名, 手机号, 余额]
                if len(row) == 3:
                    members_data[row[1]] = {"name": row[0], "balance": float(row[2])}  # 使用手机号作为键
    except FileNotFoundError:
        print("members.csv 文件未找到!")
    return members_data


# 添加商品到商品列表
def add_goods():
    product_id = entry_product_id.get()
    if product_id in goods_data:
        product_info = goods_data[product_id]
        listbox.insert(END, f"{product_id} - {product_info['name']} - {product_info['price']}")
    else:
        error_label.config(text="未找到该商品编号!")

# 删除选中的商品
def delete_goods():
    try:
        selected_item = listbox.curselection()
        if selected_item:
            listbox.delete(selected_item)
            error_label.config(text="")
        else:
            error_label.config(text="请先选择一个商品!")
    except Exception as e:
        error_label.config(text=f"删除失败: {str(e)}")

# 计算总价
def calculate_total():
    total = 0.0
    for item in listbox.get(0, END):
        price = item.split(' - ')[-1]
        total += float(price)
    return total

# 付款功能（弹出支付方式窗口）
def open_payment_window():
    total = calculate_total()
    if total == 0:
        messagebox.showwarning("警告", "请先添加商品到购物车!")
        return
    
    payment_window = Toplevel(root)
    payment_window.title("选择支付方式")
    
    label_total = ttk.Label(payment_window, text=f"总金额: {total:.2f} 元")
    label_total.pack(pady=10)

    def process_payment(payment_method):
        if payment_method == "会员支付":
            phone_number = entry_phone_number.get()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            members_data = load_members_data()  # 加载会员数据
            
            if phone_number not in members_data:
                messagebox.showwarning("错误", "未找到该会员!")
                return
            
            member_info = members_data[phone_number]
            if member_info["balance"] >= total:
                new_balance = member_info["balance"] - total
                log_filename = f"{phone_number}.log"
                # 更新余额
                update_member_balance(phone_number, new_balance)
                with open(log_filename, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"{current_time} {phone_number} 花费 {total} 元\n")
                messagebox.showinfo("支付成功", "会员支付成功!")
                listbox.delete(0, END)  # 清除商品列表
            else:
                messagebox.showwarning("余额不足", "您的余额不足，请选择其他支付方式或充值!")
        
        elif payment_method == "现金支付":
            messagebox.showinfo("支付成功", "现金支付成功!")
            listbox.delete(0, END)  # 清除商品列表

    # 选择支付方式
    btn_cash = ttk.Button(payment_window, text="现金支付", command=lambda: process_payment("现金支付"))
    btn_cash.pack(pady=5)

    btn_member = ttk.Button(payment_window, text="会员支付", command=lambda: process_payment("会员支付"))
    btn_member.pack(pady=5)

    # 会员支付需要输入手机号
    label_phone_number = ttk.Label(payment_window, text="请输入手机号:")
    label_phone_number.pack(pady=5)
    
    entry_phone_number = ttk.Entry(payment_window)
    entry_phone_number.pack(pady=5)

    # 微信支付和支付宝支付按钮
    btn_wechat = ttk.Button(payment_window, text="微信支付", command=lambda: show_payment_codes("wechatpay.png", total))
    btn_wechat.pack(pady=5)

    btn_alipay = ttk.Button(payment_window, text="支付宝支付", command=lambda: show_payment_codes("alipay.png", total))
    btn_alipay.pack(pady=5)

def show_payment_codes(image_path, total):
    payment_code_window = Toplevel(root)
    payment_code_window.title("付款码")
    
    # 显示付款金额
    label_amount = ttk.Label(payment_code_window, text=f"需付款金额: {total:.2f} 元")
    label_amount.pack(pady=10)
    
    # 完成按钮
    buttonFinish = ttk.Button(payment_code_window, text="完成", command=payment_code_window.destroy)
    buttonFinish.pack(pady=10)
    
    # 加载并显示付款码图片
    try:
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        label_image = Label(payment_code_window, image=photo)
        label_image.image = photo  # 保持引用
        label_image.pack(pady=10)
    except Exception as e:
        messagebox.showerror("错误", f"无法加载付款码图片: {e}")


# 更新会员余额
def update_member_balance(phone_number, new_balance):
    members_data = load_members_data()
    if phone_number in members_data:
        members_data[phone_number]["balance"] = new_balance
        
        # 将更新后的数据保存回文件
        with open('members.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name', 'phone', 'balance'])  # 写入表头
            for phone, info in members_data.items():
                writer.writerow([info["name"], phone, info["balance"]])

# 读取商品数据
goods_data = load_goods_data()

# 商品输入框和按钮
frame_input = ttk.Frame(root)
frame_input.pack(pady=10)

label_product_id = ttk.Label(frame_input, text="商品编号:")
label_product_id.grid(row=0, column=0, padx=10)

entry_product_id = ttk.Entry(frame_input)
entry_product_id.grid(row=0, column=1, padx=10)

btn_add = ttk.Button(frame_input, text="添加商品", command=add_goods)
btn_add.grid(row=0, column=2, padx=10)

# 商品列表
frame_list = ttk.Frame(root)
frame_list.pack(pady=10)

label_goods_list = ttk.Label(frame_list, text="商品列表:")
label_goods_list.grid(row=0, column=0, padx=10)

listbox = Listbox(frame_list, width=50, height=10)
listbox.grid(row=1, column=0, padx=10, pady=5)

btn_delete = ttk.Button(frame_list, text="删除", command=delete_goods)
btn_delete.grid(row=2, column=0, pady=5)

# 付款按钮
btn_payment = ttk.Button(root, text="付款", command=open_payment_window)
btn_payment.pack(pady=10)

# 错误提示标签
error_label = ttk.Label(root, text="", foreground="red")
error_label.pack(pady=5)

# 运行主循环
root.mainloop()
