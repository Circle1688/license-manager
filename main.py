import json
from datetime import datetime
from pathlib import Path
import gradio as gr

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base

from license import License

# 创建数据库引擎和基类
Base = declarative_base()

# 定义数据模型
class ManagerData(Base):
    __tablename__ = 'manager_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    username = Column(String(50))
    password = Column(String(100))

class LicenseData(Base):
    __tablename__ = 'license_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(50))
    product = Column(String(50))
    category = Column(String(50))
    machine_code = Column(Text)
    max_usage = Column(Integer)
    day = Column(Integer)
    activate_code = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# 创建数据库连接
engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)


# 1. 定义验证函数
def check_login(username, password):
    try:
        # 连接数据库
        session = Session()

        manager = session.query(ManagerData).filter_by(username=username, password=password).first()

        if manager:
            return True  # 登录成功
        return False  # 登录失败

    except Exception as e:
        print(f"数据库错误: {e}")
        return False

def add_license(user, product, category, machine_code, max_usage, day, activate_code):
    session = Session()

    try:

        # 创建新记录
        new_license = LicenseData(
            user=user,
            product=product,
            category=category,
            machine_code=machine_code,
            max_usage=max_usage,
            day=day,
            activate_code=activate_code
        )

        # 添加到会话并提交
        session.add(new_license)
        session.commit()

    except Exception as e:
        session.rollback()
        return f"插入数据时出错: {str(e)}"
    finally:
        session.close()

def get_all_licenses():
    session = Session()

    try:
        # 查询所有数据
        all_data = session.query(LicenseData).order_by(LicenseData.created_at.desc()).all()

        # 转换为列表格式供Gradio表格显示
        if len(all_data) == 0:
            return [[]]
        data_list = []
        for item in all_data:
            data_list.append([
                item.id,
                item.user,
                item.product,
                item.category,
                item.machine_code,
                item.max_usage,
                item.day,
                item.activate_code,
                item.created_at.strftime("%Y-%m-%d %H:%M")
            ])

        return data_list
    except Exception as e:
        return [[]]
    finally:
        session.close()



def on_license_category_change(category):
    if category == "standalone":
        return [
            gr.update(interactive=True),
            gr.update(interactive=False)
        ]
    else:
        return [
            gr.update(interactive=False),
            gr.update(interactive=True)
        ]

def get_selected_license_category(evt: gr.SelectData):
    return evt.index


def generate(user, category, license_category, machine_code, max_usage, days):
    if license_category == 0:
        activate_code = License.generate(category, machine_code, days)
        add_license(user, category, "standalone", machine_code, None, days, activate_code)
    else:
        activate_code = License.generate_floating(category, max_usage, days)
        add_license(user, category, "floating", None, max_usage, days, activate_code)

    data = get_all_licenses()
    return activate_code, data

with gr.Blocks(title="授权管理系统") as demo:
    gr.Markdown("# 授权管理系统")
    p = Path("PEM")
    folders = [item.name for item in p.iterdir() if item.is_dir()]

    user_textbox = gr.Textbox(
        lines=1,
        label="客户",
        placeholder="请输入客户名称",
    )

    category = gr.Radio(choices=folders, label="产品", value=folders[0])

    # license_category = gr.Radio(choices=['standalone', 'floating'], label="许可类型", value="standalone")

    license_category = gr.State(value=0)

    with gr.Tabs():
        with gr.Tab("单机授权", id="standalone") as standalone:
            machine_code_textbox = gr.Textbox(
                lines=1,
                label="机器码",
                placeholder="请输入机器码",
            )
        with gr.Tab("浮动授权", id="floating") as floating:
            max_usage = gr.Number(
                label="浮动并发数",
                precision=0,
                value=1,
                step=1,
                minimum=1,
            )

    standalone.select(
        fn=get_selected_license_category,
        outputs=[license_category]
    )

    floating.select(
        fn=get_selected_license_category,
        outputs=[license_category]
    )

    days = gr.Number(
        label="有效期（天）",
        precision=0,
        value=7,
        step=1,
        minimum=1
    )
    gen_button = gr.Button("生成激活码", variant="primary")

    output_textbox = gr.Textbox(
        label="激活码",
        buttons=['copy']
    )

    initial_data = get_all_licenses()
    # 数据显示表格
    data_table = gr.Dataframe(
        value=initial_data,
        type="array",
        headers=["ID", "客户", "产品", "许可类型", "单机机器码", "浮动并发数", "有效期（天）", "激活码", "授权时间"],
        label="授权数据表",
        interactive=True,
        wrap=True,
        datatype='auto',
        column_count=9,
        static_columns=[0,1,2,3,4,5,6,8]
    )
    refresh_button = gr.Button("刷新数据库")

    gen_button.click(
        generate,
        inputs=[user_textbox, category, license_category, machine_code_textbox, max_usage, days],
        outputs=[output_textbox, data_table]
    )

    refresh_button.click(
        get_all_licenses,
        outputs=[data_table]
    )

demo.launch(server_name="0.0.0.0", auth=check_login)
# demo.launch(server_name="0.0.0.0")
