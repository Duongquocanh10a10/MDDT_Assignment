namespace WinFormsApp1;

public class HangHoa
{
  public List<HangHoa> HangHoas = new();
  private string mahang;
  private string tenhang;
  private string dvt;
  private float dongia;
  public string MaHang { get; set; }
  public string TenHang { get; set; }
  public string DVT { get; set; }
  public string DonGiaMacDInh { get; set; }
  public string DonGia { get; set; }

  public void HienThi()
  {
    
  }

  public void HienThi(string MaHang, string TenHang, string DVT, float DonGia)
  {
    this.mahang = MaHang;
    this.tenhang = TenHang;
    this.dvt = DVT;
    this.dongia = DonGia;
  }
  
}