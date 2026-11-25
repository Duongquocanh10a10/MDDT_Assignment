namespace WinFormsApp1;

public partial class Bai2 : Form
{
    HangHoa HH=new HangHoa();
    private int SoLuong;
    
    public Bai2()
    {
        InitializeComponent();
    }

    private void Bai2_Load(object sender, EventArgs e)
    {
       
    }

    private void listBox1_SelectedIndexChanged(object sender, EventArgs e)
    {
       
    }

    private void checkBox2_CheckedChanged(object sender, EventArgs e)
    {
       
    }


    private void checkBox1_CheckedChanged(object sender, EventArgs e)
    {
        
    }


    private void label5_Click(object sender, EventArgs e)
    {
        
    }

    private void label2_Click(object sender, EventArgs e)
    {
        throw new System.NotImplementedException();
    }

    private void textBox1_TextChanged(object sender, EventArgs e)
    {
        try
        {
            HH.DonGia = tDonGia.Text;
        }
        catch
        {
            
        }
    }


    private void numericUpDown1_ValueChanged(object sender, EventArgs e)
    {
        this.SoLuong = (int)number.Value;
    }
}