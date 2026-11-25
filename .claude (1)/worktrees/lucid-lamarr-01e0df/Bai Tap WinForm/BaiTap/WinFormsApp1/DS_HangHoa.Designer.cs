using System.ComponentModel;

namespace WinFormsApp1;

partial class DS_HangHoa
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
        listView1 = new System.Windows.Forms.ListView();
        label1 = new System.Windows.Forms.Label();
        label2 = new System.Windows.Forms.Label();
        label3 = new System.Windows.Forms.Label();
        label4 = new System.Windows.Forms.Label();
        textBox2 = new System.Windows.Forms.TextBox();
        textBox3 = new System.Windows.Forms.TextBox();
        textBox4 = new System.Windows.Forms.TextBox();
        listBox1 = new System.Windows.Forms.ListBox();
        SuspendLayout();
        // 
        // listView1
        // 
        listView1.Location = new System.Drawing.Point(12, 187);
        listView1.Name = "listView1";
        listView1.Size = new System.Drawing.Size(776, 242);
        listView1.TabIndex = 0;
        listView1.UseCompatibleStateImageBehavior = false;
        // 
        // label1
        // 
        label1.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label1.Location = new System.Drawing.Point(33, 26);
        label1.Name = "label1";
        label1.Size = new System.Drawing.Size(86, 28);
        label1.TabIndex = 1;
        label1.Text = "Mã Hàng";
        label1.Click += label1_Click;
        // 
        // label2
        // 
        label2.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label2.Location = new System.Drawing.Point(216, 26);
        label2.Name = "label2";
        label2.Size = new System.Drawing.Size(100, 23);
        label2.TabIndex = 2;
        label2.Text = "Tên Hàng";
        // 
        // label3
        // 
        label3.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label3.Location = new System.Drawing.Point(407, 26);
        label3.Name = "label3";
        label3.Size = new System.Drawing.Size(101, 23);
        label3.TabIndex = 3;
        label3.Text = "Đơn Vị Tính";
        // 
        // label4
        // 
        label4.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)0));
        label4.Location = new System.Drawing.Point(611, 26);
        label4.Name = "label4";
        label4.Size = new System.Drawing.Size(100, 23);
        label4.TabIndex = 4;
        label4.Text = "Đơn Giá";
        // 
        // textBox2
        // 
        textBox2.Location = new System.Drawing.Point(216, 70);
        textBox2.Name = "textBox2";
        textBox2.Size = new System.Drawing.Size(169, 27);
        textBox2.TabIndex = 6;
        // 
        // textBox3
        // 
        textBox3.Location = new System.Drawing.Point(407, 70);
        textBox3.Name = "textBox3";
        textBox3.Size = new System.Drawing.Size(166, 27);
        textBox3.TabIndex = 7;
        // 
        // textBox4
        // 
        textBox4.Location = new System.Drawing.Point(611, 70);
        textBox4.Name = "textBox4";
        textBox4.Size = new System.Drawing.Size(177, 27);
        textBox4.TabIndex = 8;
        // 
        // listBox1
        // 
        listBox1.FormattingEnabled = true;
        listBox1.Items.AddRange(new object[] { "MHVN 1", "MHVN 2", "MHVN 3" });
        listBox1.Location = new System.Drawing.Point(33, 70);
        listBox1.Name = "listBox1";
        listBox1.Size = new System.Drawing.Size(147, 24);
        listBox1.TabIndex = 9;
        listBox1.SelectedIndexChanged += listBox1_SelectedIndexChanged;
        // 
        // DS_HangHoa
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(8F, 20F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        ClientSize = new System.Drawing.Size(800, 450);
        Controls.Add(listBox1);
        Controls.Add(textBox4);
        Controls.Add(textBox3);
        Controls.Add(textBox2);
        Controls.Add(label4);
        Controls.Add(label3);
        Controls.Add(label2);
        Controls.Add(label1);
        Controls.Add(listView1);
        Text = "DS_HangHoa";
        ResumeLayout(false);
        PerformLayout();
    }

    private System.Windows.Forms.ListBox listBox1;

    private System.Windows.Forms.TextBox textBox2;
    private System.Windows.Forms.TextBox textBox3;
    private System.Windows.Forms.TextBox textBox4;

    private System.Windows.Forms.Label label2;
    private System.Windows.Forms.Label label3;
    private System.Windows.Forms.Label label4;

    private System.Windows.Forms.Label label1;

    private System.Windows.Forms.ListView listView1;

    #endregion
}