using System.ComponentModel;

namespace WinFormsApp1;

partial class Bai2
{
    /// <summary>
    /// Required designer variable.
    /// </summary>
    private IContainer components = null;

    /// <summary>
    /// Clean up any resources being used.
    /// </summary>
    /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }

        base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    /// <summary>
    /// Required method for Designer support - do not modify
    /// the contents of this method with the code editor.
    /// </summary>
    private void InitializeComponent()
    {
        button1 = new System.Windows.Forms.Button();
        label1 = new System.Windows.Forms.Label();
        label2 = new System.Windows.Forms.Label();
        label3 = new System.Windows.Forms.Label();
        label4 = new System.Windows.Forms.Label();
        listBox1 = new System.Windows.Forms.ListBox();
        tDonGia = new System.Windows.Forms.TextBox();
        groupBox1 = new System.Windows.Forms.GroupBox();
        checkBox2 = new System.Windows.Forms.CheckBox();
        checkBox1 = new System.Windows.Forms.CheckBox();
        SumList = new System.Windows.Forms.Label();
        button2 = new System.Windows.Forms.Button();
        button3 = new System.Windows.Forms.Button();
        listBox2 = new System.Windows.Forms.ListBox();
        number = new System.Windows.Forms.NumericUpDown();
        groupBox1.SuspendLayout();
        ((System.ComponentModel.ISupportInitialize)number).BeginInit();
        SuspendLayout();
        // 
        // button1
        // 
        button1.Location = new System.Drawing.Point(283, 345);
        button1.Name = "button1";
        button1.Size = new System.Drawing.Size(114, 31);
        button1.TabIndex = 0;
        button1.Text = "Tính Tiền";
        button1.UseVisualStyleBackColor = true;
        // 
        // label1
        // 
        label1.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label1.Location = new System.Drawing.Point(45, 114);
        label1.Name = "label1";
        label1.Size = new System.Drawing.Size(214, 35);
        label1.TabIndex = 1;
        label1.Text = "Tên Hàng";
        // 
        // label2
        // 
        label2.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label2.Location = new System.Drawing.Point(45, 169);
        label2.Name = "label2";
        label2.Size = new System.Drawing.Size(141, 22);
        label2.TabIndex = 2;
        label2.Text = "Đơn Giá";
        label2.Click += label2_Click;
        // 
        // label3
        // 
        label3.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label3.Location = new System.Drawing.Point(44, 215);
        label3.Name = "label3";
        label3.Size = new System.Drawing.Size(169, 41);
        label3.TabIndex = 3;
        label3.Text = "Số Lượng";
        // 
        // label4
        // 
        label4.Font = new System.Drawing.Font("Times New Roman", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label4.Location = new System.Drawing.Point(12, 411);
        label4.Name = "label4";
        label4.Size = new System.Drawing.Size(299, 49);
        label4.TabIndex = 4;
        label4.Text = "Số Tiền Cần Thành Toán :";
        // 
        // listBox1
        // 
        listBox1.FormattingEnabled = true;
        listBox1.Items.AddRange(new object[] { "Chuột", "Máy in", "Bàn Phím" });
        listBox1.Location = new System.Drawing.Point(127, 114);
        listBox1.Name = "listBox1";
        listBox1.Size = new System.Drawing.Size(201, 24);
        listBox1.TabIndex = 5;
        listBox1.SelectedIndexChanged += listBox1_SelectedIndexChanged;
        // 
        // tDonGia
        // 
        tDonGia.Location = new System.Drawing.Point(127, 164);
        tDonGia.Name = "tDonGia";
        tDonGia.Size = new System.Drawing.Size(201, 27);
        tDonGia.TabIndex = 6;
        tDonGia.TextChanged += textBox1_TextChanged;
        // 
        // groupBox1
        // 
        groupBox1.Controls.Add(checkBox2);
        groupBox1.Controls.Add(checkBox1);
        groupBox1.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        groupBox1.Location = new System.Drawing.Point(127, 248);
        groupBox1.Name = "groupBox1";
        groupBox1.Size = new System.Drawing.Size(201, 79);
        groupBox1.TabIndex = 8;
        groupBox1.TabStop = false;
        groupBox1.Text = "Hình Thức Thanh Toán";
        groupBox1.Visible = false;
        // 
        // checkBox2
        // 
        checkBox2.Location = new System.Drawing.Point(6, 49);
        checkBox2.Name = "checkBox2";
        checkBox2.Size = new System.Drawing.Size(144, 24);
        checkBox2.TabIndex = 1;
        checkBox2.Text = "Chuyển Khoản";
        checkBox2.UseVisualStyleBackColor = true;
        checkBox2.CheckedChanged += checkBox2_CheckedChanged;
        // 
        // checkBox1
        // 
        checkBox1.Location = new System.Drawing.Point(6, 26);
        checkBox1.Name = "checkBox1";
        checkBox1.Size = new System.Drawing.Size(104, 30);
        checkBox1.TabIndex = 0;
        checkBox1.Text = "Tiền Mặt";
        checkBox1.UseVisualStyleBackColor = true;
        checkBox1.CheckedChanged += checkBox1_CheckedChanged;
        // 
        // SumList
        // 
        SumList.Font = new System.Drawing.Font("Times New Roman", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        SumList.Location = new System.Drawing.Point(227, 411);
        SumList.Name = "SumList";
        SumList.Size = new System.Drawing.Size(170, 21);
        SumList.TabIndex = 10;
        SumList.Text = "0";
        SumList.Click += label5_Click;
        // 
        // button2
        // 
        button2.Location = new System.Drawing.Point(12, 346);
        button2.Name = "button2";
        button2.Size = new System.Drawing.Size(111, 28);
        button2.TabIndex = 11;
        button2.Text = "Reset";
        button2.UseVisualStyleBackColor = true;
        // 
        // button3
        // 
        button3.Location = new System.Drawing.Point(143, 347);
        button3.Name = "button3";
        button3.Size = new System.Drawing.Size(115, 26);
        button3.TabIndex = 12;
        button3.Text = "Xác Nhận";
        button3.UseVisualStyleBackColor = true;
        // 
        // listBox2
        // 
        listBox2.FormattingEnabled = true;
        listBox2.Location = new System.Drawing.Point(423, 50);
        listBox2.Name = "listBox2";
        listBox2.Size = new System.Drawing.Size(246, 324);
        listBox2.TabIndex = 13;
        // 
        // number
        // 
        number.Location = new System.Drawing.Point(127, 210);
        number.Name = "number";
        number.Size = new System.Drawing.Size(201, 27);
        number.TabIndex = 14;
        number.ValueChanged += numericUpDown1_ValueChanged;
        // 
        // Bai2
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(8F, 20F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        ClientSize = new System.Drawing.Size(701, 450);
        Controls.Add(number);
        Controls.Add(listBox2);
        Controls.Add(button3);
        Controls.Add(button2);
        Controls.Add(SumList);
        Controls.Add(groupBox1);
        Controls.Add(tDonGia);
        Controls.Add(listBox1);
        Controls.Add(label4);
        Controls.Add(label3);
        Controls.Add(label2);
        Controls.Add(label1);
        Controls.Add(button1);
        Text = "Bai1";
        Load += Bai2_Load;
        groupBox1.ResumeLayout(false);
        ((System.ComponentModel.ISupportInitialize)number).EndInit();
        ResumeLayout(false);
        PerformLayout();
    }

    private System.Windows.Forms.NumericUpDown number;

    private System.Windows.Forms.ListBox listBox2;

    private System.Windows.Forms.Button button3;

    private System.Windows.Forms.Button button2;

    private System.Windows.Forms.Label SumList;

    private System.Windows.Forms.CheckBox checkBox1;
    private System.Windows.Forms.CheckBox checkBox2;

    private System.Windows.Forms.GroupBox groupBox1;

    private System.Windows.Forms.ListBox listBox1;

    private System.Windows.Forms.TextBox tDonGia;

    private System.Windows.Forms.Label label2;
    private System.Windows.Forms.Label label3;
    private System.Windows.Forms.Label label4;

    private System.Windows.Forms.Label label1;

    private System.Windows.Forms.Button button1;

    #endregion
}